import asyncio
import contextvars
import functools
import inspect
import re
from typing import Optional, List, Callable, Awaitable, Any

from hypothesis import settings, seed, given, Verbosity
from hypothesis.database import InMemoryExampleDatabase
from hypothesis.reporting import with_reporter
from hypothesis.strategies import data, DataObject

from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
    TestCaseCheatcodeFactory,
)
from protostar.commands.test.fuzzing.strategy_selector import StrategySelector
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_context import TestContextHintLocal
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.testing_seed import current_testing_seed
from protostar.utils.data_transformer_facade import DataTransformerFacade


HYPOTHESIS_VERBOSITY = Verbosity.normal
"""
Change this value to ``Verbosity.verbose`` while debugging Hypothesis adapter code.
"""


def is_fuzz_test(function_name: str, state: TestExecutionState) -> bool:
    abi = state.contract.abi
    params = DataTransformerFacade.get_function_parameters(abi, function_name)
    return bool(params)


class FuzzTestExecutionEnvironment(TestExecutionEnvironment):
    def __init__(self, state: TestExecutionState):
        super().__init__(state)

    async def invoke(self, function_name: str) -> Optional[ExecutionResourcesSummary]:
        abi = self.state.contract.abi
        parameters = DataTransformerFacade.get_function_parameters(abi, function_name)
        assert (
            parameters
        ), f"{self.__class__.__name__} expects at least one function parameter."

        self.set_cheatcodes(
            TestCaseCheatcodeFactory(
                state=self.state,
                expect_revert_context=self._expect_revert_context,
                finish_hook=self._finish_hook,
            )
        )

        self.set_custom_hint_locals([TestContextHintLocal(self.state.context)])

        execution_resources: List[ExecutionResourcesSummary] = []

        database = InMemoryExampleDatabase()
        strategy_selector = StrategySelector(parameters)

        # NOTE: Hypothesis' ``reporter`` global is a thread local variable.
        #   Because we are running Hypothesis from separate thread, and the test itself is
        #   running in a separate thread executor, we must set the ``reporter`` each first time
        #   we invoke Hypothesis code in new thread.

        @seed(current_testing_seed())
        @settings(
            database=database,
            deadline=None,
            print_blob=False,
            verbosity=HYPOTHESIS_VERBOSITY,
        )
        @given(data_object=data())
        async def test(data_object: DataObject):
            with with_reporter(protostar_reporter):
                inputs = {}
                for param in strategy_selector.parameter_names:
                    search_strategy = strategy_selector.search_strategies[param]
                    inputs[param] = data_object.draw(search_strategy, label=param)

                try:
                    run_ers = await self.invoke_test_case(function_name, **inputs)
                    if run_ers is not None:
                        execution_resources.append(run_ers)
                except ReportedException as reported_ex:
                    raise HypothesisEscapeError(reported_ex) from reported_ex

        test.hypothesis.inner_test = wrap_in_sync(test.hypothesis.inner_test)  # type: ignore

        def test_thread():
            with with_reporter(protostar_reporter):
                test()

        try:
            await to_thread(test_thread)
        except HypothesisEscapeError as escape_err:
            raise escape_err.inner

        return ExecutionResourcesSummary.sum(execution_resources)


class HypothesisEscapeError(Exception):
    def __init__(self, inner: ReportedException):
        super().__init__()
        self.inner = inner


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


JAMMING_MESSAGE = re.compile(r"^Draw|^(Trying|Falsifying) example:")


def protostar_reporter(message: str):
    if HYPOTHESIS_VERBOSITY > Verbosity.normal or not JAMMING_MESSAGE.match(message):
        print(message)
