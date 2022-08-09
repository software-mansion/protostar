from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
    FuzzTestExecutionResult,
)
from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.test_case_runners.test_case_runner import (
    TestCaseRunner,
)
from protostar.commands.test.test_cases import (
    FailedFuzzTestCaseResult,
    FailedTestCaseResult,
    FuzzResult,
    PassedFuzzTestCaseResult,
    TestResult,
)
from protostar.commands.test.test_environment_exceptions import ReportedException


class FuzzTestCaseRunner(TestCaseRunner[FuzzTestExecutionResult]):
    def __init__(
        self,
        fuzz_test_execution_environment: FuzzTestExecutionEnvironment,
        dependencies: TestCaseRunner.Dependencies,
    ) -> None:
        super().__init__(dependencies)
        self._fuzz_test_execution_environment = fuzz_test_execution_environment

    async def _run_test_case(self, test_case_name: str) -> FuzzTestExecutionResult:
        return await self._fuzz_test_execution_environment.invoke(test_case_name)

    def _map_execution_result_to_passed_test_result(
        self,
        execution_result: FuzzTestExecutionResult,
        test_case_name: str,
        execution_time: float,
    ) -> TestResult:
        passed_test_case_result = super()._map_execution_result_to_passed_test_result(
            execution_result, test_case_name, execution_time
        )
        return PassedFuzzTestCaseResult.from_passed_test_case_result(
            passed_test_case_result,
            fuzz_result=FuzzResult(fuzz_runs_count=execution_result.fuzz_runs_count),
        )

    def _map_reported_exception_to_failed_test_result(
        self,
        reported_exception: ReportedException,
        test_case_name: str,
        execution_time: float,
    ) -> FailedTestCaseResult:
        failed_test_case_result = super()._map_reported_exception_to_failed_test_result(
            reported_exception, test_case_name, execution_time
        )

        metadata = reported_exception.metadata
        if len(metadata) > 0 and isinstance(metadata[0], FuzzInputExceptionMetadata):
            fuzz_runs_count = reported_exception.execution_info["fuzz_runs"]
            assert isinstance(fuzz_runs_count, int)

            return FailedFuzzTestCaseResult.from_failed_test_case_result(
                failed_test_case_result=failed_test_case_result,
                fuzz_result=FuzzResult(fuzz_runs_count=fuzz_runs_count),
            )

        assert False, "ReportedException must include fuzz metadata"
