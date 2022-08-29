import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List

from hypothesis import given, seed, settings
from hypothesis.database import ExampleDatabase, InMemoryExampleDatabase
from hypothesis.errors import InvalidArgument
from hypothesis.reporting import with_reporter
from hypothesis.strategies import SearchStrategy
from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    AssumeCheatcode,
    RejectCheatcode,
)
from protostar.commands.test.environments.test_execution_environment import (
    TestCaseCheatcodeFactory,
    TestExecutionEnvironment,
    TestExecutionResult,
)
from protostar.commands.test.fuzzing.exceptions import HypothesisRejectException
from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.fuzzing.hypothesis.aio import to_thread, wrap_in_sync
from protostar.commands.test.fuzzing.hypothesis.reporter import (
    HYPOTHESIS_VERBOSITY,
    protostar_reporter,
)
from protostar.commands.test.fuzzing.hypothesis.runs_counter import RunsCounter
from protostar.commands.test.fuzzing.strategy_collector import collect_search_strategies
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_environment_exceptions import (
    CheatcodeException,
    ReportedException,
)
from protostar.commands.test.testing_seed import TestingSeed
from protostar.starknet.cheatcode import Cheatcode
from protostar.utils.abi import get_function_parameters


@dataclass
class FuzzTestExecutionResult(TestExecutionResult):
    fuzz_runs_count: int


class FuzzTestExecutionEnvironment(TestExecutionEnvironment):
    def __init__(self, state: TestExecutionState):
        super().__init__(state)
        self.initial_state = state

    async def invoke(self, function_name: str) -> FuzzTestExecutionResult:
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

        execution_resources: List[ExecutionResourcesSummary] = []

        database = InMemoryExampleDatabase()
        runs_counter = RunsCounter(budget=self.state.config.fuzz_max_examples)

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

    def build_and_run_test(
        self,
        function_name: str,
        database: ExampleDatabase,
        execution_resources: List[ExecutionResourcesSummary],
        runs_counter: RunsCounter,
        given_strategies: Dict[str, SearchStrategy],
    ):
        try:

            @seed(TestingSeed.current())
            @settings(
                database=database,
                deadline=None,
                max_examples=runs_counter.available_runs,
                print_blob=False,
                report_multiple_bugs=False,
                verbosity=HYPOTHESIS_VERBOSITY,
            )
            @given(**given_strategies)
            async def test(**inputs: Any):
                self.fork_state_for_test()

                run_no = next(runs_counter)
                with self.state.output_recorder.redirect(("test", run_no)):
                    with with_reporter(protostar_reporter):
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

            # NOTE: The ``test`` function does not expect any arguments at this point,
            #   because the @given decorator provides all of them behind the scenes.
            test()
        except InvalidArgument as ex:
            # This exception is sometimes raised by Hypothesis during runtime when user messes up
            # strategy arguments. For example, invalid range for `integers` strategy is caught here.
            raise CheatcodeException("given", str(ex)) from ex


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
