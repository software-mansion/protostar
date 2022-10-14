import dataclasses
from asyncio import to_thread
from dataclasses import dataclass
from typing import Any, Dict, List, Callable
import logging

from hypothesis import given, seed, settings, example, Phase
from hypothesis.database import ExampleDatabase, InMemoryExampleDatabase
from hypothesis.errors import InvalidArgument
from hypothesis.reporting import with_reporter
from hypothesis.strategies import SearchStrategy
from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.starknet import ReportedException
from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import AssumeCheatcode, RejectCheatcode
from protostar.testing.fuzzing.exceptions import HypothesisRejectException, FuzzingError
from protostar.testing.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.testing.fuzzing.hypothesis.aio import wrap_in_sync
from protostar.testing.fuzzing.hypothesis.reporter import (
    HYPOTHESIS_VERBOSITY,
    protostar_reporter,
)
from protostar.testing.fuzzing.hypothesis.runs_counter import RunsCounter
from protostar.testing.fuzzing.strategy_collector import collect_search_strategies
from protostar.testing.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.testing.starkware.test_execution_state import TestExecutionState
from protostar.starknet.abi import get_function_parameters
from protostar.protostar_exception import ProtostarException


from .test_execution_environment import (
    TestCaseCheatcodeFactory,
    TestExecutionEnvironment,
    TestExecutionResult,
)


@dataclass
class FuzzTestExecutionResult(TestExecutionResult):
    fuzz_runs_count: int


class FuzzTestExecutionEnvironment(TestExecutionEnvironment):
    def __init__(self, state: TestExecutionState):
        super().__init__(state)
        if self.state.config.profiling:
            raise ProtostarException("Fuzz tests cannot be profiled")
        self.initial_state = state
        self._logger = logging.getLogger(__name__)

    async def execute(self, function_name: str) -> FuzzTestExecutionResult:
        abi = self.state.contract.abi
        parameters = get_function_parameters(abi, function_name)
        assert (
            parameters
        ), f"{self.__class__.__name__} expects at least one function parameter."

        execution_resources: List[ExecutionResourcesSummary] = []

        database = InMemoryExampleDatabase()
        runs_counter = RunsCounter(budget=self.state.config.fuzz_max_examples)

        if (
            not self.state.config.fuzz_examples
            and not self.state.config.fuzz_declared_strategies
        ):
            self._logger.warning(
                "not providing the test data is deprecated and will break test cases in the future releases, "
                "please use one of the following cheatcodes in the setup function in order to "
                "explicitly provide data to be tested: \n- example\n- given"
            )
            # todo raise an error in future releases

        given_strategies = collect_search_strategies(
            declared_strategies=self.state.config.fuzz_declared_strategies,
            parameters=parameters,
        )

        # NOTE: Hypothesis' ``reporter`` global is a thread local variable.
        #   Because we are running Hypothesis from separate thread, and the test itself is
        #   running in a separate thread executor, we must set the ``reporter`` each first time
        #   we invoke Hypothesis code in new thread.

        def test_thread():
            with with_reporter(protostar_reporter):
                self.build_and_run_test(
                    function_name=function_name,
                    database=database,
                    execution_resources=execution_resources,
                    runs_counter=runs_counter,
                    given_strategies=given_strategies,
                )

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

    def set_cheatcodes_for_test(self):
        """
        Cheatcodes and hint locals have to be built on each fuzz test run to avoid sharing a state.
        """

        self.set_cheatcodes(
            FuzzTestCaseCheatcodeFactory(
                state=self.state,
                expect_revert_context=self._expect_revert_context,
                finish_hook=self._finish_hook,
            )
        )

    def decorate_with_examples(self, target_func: Callable):
        func = target_func
        for ex in reversed(self.state.config.fuzz_examples):
            func = example(**ex)(func)
        return func

    def build_and_run_test(
        self,
        function_name: str,
        database: ExampleDatabase,
        execution_resources: List[ExecutionResourcesSummary],
        runs_counter: RunsCounter,
        given_strategies: Dict[str, SearchStrategy],
    ):
        try:
            settings_instance = settings(
                database=database,
                deadline=None,
                max_examples=runs_counter.available_runs,
                print_blob=False,
                report_multiple_bugs=False,
                verbosity=HYPOTHESIS_VERBOSITY,
            )
            if (
                not self.state.config.fuzz_declared_strategies
                and self.state.config.fuzz_examples
            ):
                settings_instance = settings(
                    settings_instance, phases=(Phase.explicit,)
                )

            @self.decorate_with_examples
            @seed(self.state.config.seed)
            @settings_instance
            @given(**given_strategies)
            async def test(**inputs: Any):
                self.fork_state_for_test()
                self.set_cheatcodes_for_test()

                run_no = next(runs_counter)
                with self.state.output_recorder.redirect(("test", run_no)):
                    with with_reporter(protostar_reporter):
                        try:
                            this_run_resources = await self.execute_test_case(
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

            # NOTE: The ``test`` function does not expect any arguments at this point,
            #   because the @given decorator provides all of them behind the scenes.
            test()
        except InvalidArgument as ex:
            # This exception is sometimes raised by Hypothesis during runtime when user messes up
            # strategy arguments. For example, invalid range for `integers` strategy is caught here.
            raise FuzzingError(str(ex)) from ex


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


class FuzzTestCaseCheatcodeFactory(TestCaseCheatcodeFactory):
    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        return [
            *super().build_cheatcodes(syscall_dependencies, internal_calls),
            RejectCheatcode(syscall_dependencies),
            AssumeCheatcode(syscall_dependencies),
        ]
