import asyncio
import contextvars
import dataclasses
import functools
import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

from hypothesis import Verbosity, given, seed, settings
from hypothesis.database import InMemoryExampleDatabase
from hypothesis.reporting import with_reporter
from hypothesis.strategies import DataObject, data
from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import AssumeCheatcode, RejectCheatcode
from protostar.commands.test.cheatcodes.reflect.cairo_struct import CairoStructHintLocal
from protostar.commands.test.environments.test_execution_environment import (
    TestCaseCheatcodeFactory,
    TestExecutionEnvironment,
    TestExecutionResult,
)
from protostar.commands.test.fuzzing.exceptions import HypothesisRejectException
from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.fuzzing.strategy_selector import StrategySelector
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_context import TestContextHintLocal
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.testing_seed import TestingSeed
from protostar.starknet.cheatcode import Cheatcode
from protostar.utils.abi import get_function_parameters

HYPOTHESIS_VERBOSITY = Verbosity.normal
"""
Change this value to ``Verbosity.verbose`` while debugging Hypothesis adapter code.
"""


def is_fuzz_test(function_name: str, state: TestExecutionState) -> bool:
    abi = state.contract.abi
    params = get_function_parameters(abi, function_name)
    return bool(params)


@dataclass
class FuzzConfig:
    max_examples: int = 100


@dataclass
class FuzzTestExecutionResult(TestExecutionResult):
    fuzz_runs_count: int


class FuzzTestExecutionEnvironment(TestExecutionEnvironment):
    def __init__(
        self, state: TestExecutionState, fuzz_config: Optional[FuzzConfig] = None
    ):
        super().__init__(state)
        self.initial_state = state
        self._fuzz_config = fuzz_config or FuzzConfig()

    async def invoke(self, function_name: str) -> TestExecutionResult:
        abi = self.state.contract.abi
        parameters = get_function_parameters(abi, function_name)
        assert (
            parameters
        ), f"{self.__class__.__name__} expects at least one function parameter."

        self.set_cheatcodes(
            FuzzTestCaseCheatcodeFactory(
                state=self.state,
                expect_revert_context=self._expect_revert_context,
                finish_hook=self._finish_hook,
            )
        )

        self.set_custom_hint_locals(
            [TestContextHintLocal(self.state.context), CairoStructHintLocal()]
        )

        execution_resources: List[ExecutionResourcesSummary] = []

        database = InMemoryExampleDatabase()
        strategy_selector = StrategySelector(parameters)

        runs_counter = RunsCounter()

        # NOTE: Hypothesis' ``reporter`` global is a thread local variable.
        #   Because we are running Hypothesis from separate thread, and the test itself is
        #   running in a separate thread executor, we must set the ``reporter`` each first time
        #   we invoke Hypothesis code in new thread.

        @seed(TestingSeed.current())
        @settings(
            database=database,
            deadline=None,
            print_blob=False,
            report_multiple_bugs=False,
            verbosity=HYPOTHESIS_VERBOSITY,
            max_examples=self._fuzz_config.max_examples,
        )
        @given(data_object=data())
        async def test(data_object: DataObject):
            self.fork_state_for_test()

            run_no = next(runs_counter)
            with self.state.output_recorder.redirect(("test", run_no)):
                with with_reporter(protostar_reporter):
                    inputs: Dict[str, Any] = {}
                    for param in strategy_selector.parameter_names:
                        search_strategy = strategy_selector.get_search_strategy(param)
                        inputs[param] = data_object.draw(search_strategy, label=param)

                    try:
                        this_run_resources = await self.invoke_test_case(
                            function_name, **inputs
                        )
                        if this_run_resources is not None:
                            execution_resources.append(this_run_resources)
                    except HypothesisRejectException as reject_ex:
                        raise reject_ex.unsatisfied_assumption_exc
                    except ReportedException as reported_ex:
                        raise HypothesisFailureSmugglingError(
                            error=reported_ex,
                            inputs=inputs,
                        ) from reported_ex

        test.hypothesis.inner_test = wrap_in_sync(test.hypothesis.inner_test)  # type: ignore

        def test_thread():
            with with_reporter(protostar_reporter):
                # TODO: Document how the data_object is passed to test function
                # pylint: disable=no-value-for-parameter
                test()

        try:
            with self.state.output_recorder.redirect("test"):
                await to_thread(test_thread)
        except HypothesisFailureSmugglingError as escape_err:
            escape_err.error.execution_info["fuzz_runs"] = runs_counter.count
            escape_err.error.metadata.append(
                FuzzInputExceptionMetadata(escape_err.inputs)
            )
            raise escape_err.error

        return FuzzTestExecutionResult(
            execution_resources=ExecutionResourcesSummary.sum(execution_resources),
            fuzz_runs_count=runs_counter.count,
        )

    def fork_state_for_test(self):
        """
        Some parts of execution state **must** be shared between fuzz test runs,
        so as kinda hack, we fork the state and then bring back old, shared, objects selectively.
        """

        self.state = dataclasses.replace(
            self.initial_state.fork(),
            output_recorder=self.initial_state.output_recorder,
        )


@dataclass
class HypothesisFailureSmugglingError(Exception):
    """
    Special error type which is used to smuggle failure exception and metadata from Hypothesis
    test runner to Protostar fuzz test execution environment.

    Hypothesis does not raise failure exceptions immediately while running observations, instead
    it tries to shrink input data in order to get minimal reproduction. When input data is shrunk
    (usually when ``max_examples`` setting is exhausted), Hypothesis re-raises matching exception.

    We use this fact to smuggle additional metadata about failing test case, such as inputs values
    which caused the test to fail, because apparently there is no supported way to get this from
    Hypothesis except parsing reported messages.
    """

    error: ReportedException
    inputs: Dict[str, Any]


async def to_thread(func, *args, **kwargs):
    """
    Asynchronously run function *func* in a separate thread.

    Any *args and **kwargs supplied for this function are directly passed
    to *func*. Also, the current :class:`contextvars.Context` is propagated,
    allowing context variables from the main thread to be accessed in the
    separate thread.

    Return a coroutine that can be awaited to get the eventual result of *func*.

    Borrowed from Python 3.9
    """

    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


def wrap_in_sync(func: Callable[..., Awaitable[Any]]):
    """
    Return a sync wrapper around an async function executing it in separate event loop.

    Separate event loop is used, because Hypothesis engine is running in current executor
    and is effectively blocking it.

    Partially borrowed from pytest-asyncio.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        coro = func(*args, **kwargs)
        assert inspect.isawaitable(coro)

        loop = asyncio.new_event_loop()
        task = asyncio.ensure_future(coro, loop=loop)
        try:
            loop.run_until_complete(task)
        except BaseException:
            # run_until_complete doesn't get the result from exceptions
            # that are not subclasses of `Exception`.
            # Consume all exceptions to prevent asyncio's warning from logging.
            if task.done() and not task.cancelled():
                task.exception()
            raise

    return inner


HYPOTHESIS_MSG_JAMMER_PATTERN = re.compile(r"^Draw|^(Trying|Falsifying) example:")


def protostar_reporter(message: str):
    if (
        HYPOTHESIS_VERBOSITY > Verbosity.normal
        or not HYPOTHESIS_MSG_JAMMER_PATTERN.match(message)
    ):
        print(message)


@dataclass
class RunsCounter:
    """
    A boxed integer that can be safely shared between Python threads.
    It is used to count fuzz test runs.
    """

    count: int = field(default=0)

    def __next__(self) -> int:
        self.count += 1
        return self.count


class FuzzTestCaseCheatcodeFactory(TestCaseCheatcodeFactory):
    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        return [
            *super().build(syscall_dependencies, internal_calls),
            RejectCheatcode(syscall_dependencies),
            AssumeCheatcode(syscall_dependencies),
        ]
