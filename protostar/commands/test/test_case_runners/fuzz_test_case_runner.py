from typing import Optional

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
    FuzzTestExecutionResult,
)
from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner
from protostar.commands.test.test_results import (
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
        test_case_runner_deps: TestCaseRunner.Dependencies,
    ) -> None:
        super().__init__(test_case_runner_deps)
        self._fuzz_test_execution_environment = fuzz_test_execution_environment

    async def _run_test_case(self, test_case_name: str) -> FuzzTestExecutionResult:
        return await self._fuzz_test_execution_environment.invoke(test_case_name)

    def _map_execution_result_to_passed_test_result(
        self,
        execution_result: FuzzTestExecutionResult,
        execution_metadata: TestCaseRunner.ExecutionMetadata,
    ) -> TestResult:
        passed_test_case_result = super()._map_execution_result_to_passed_test_result(
            execution_result, execution_metadata
        )
        return PassedFuzzTestCaseResult.from_passed_test_case_result(
            passed_test_case_result,
            fuzz_result=FuzzResult(fuzz_runs_count=execution_result.fuzz_runs_count),
        )

    def _map_reported_exception_to_failed_test_result(
        self,
        reported_exception: ReportedException,
        execution_metadata: TestCaseRunner.ExecutionMetadata,
    ) -> FailedTestCaseResult:
        failed_test_case_result = super()._map_reported_exception_to_failed_test_result(
            reported_exception, execution_metadata
        )
        fuzz_result = self._map_reported_exception_to_fuzz_result(reported_exception)
        if fuzz_result:
            return FailedFuzzTestCaseResult.from_failed_test_case_result(
                failed_test_case_result,
                fuzz_result,
            )
        return FailedFuzzTestCaseResult.from_failed_test_case_result(
            failed_test_case_result, fuzz_result=None
        )

    @staticmethod
    def _map_reported_exception_to_fuzz_result(
        reported_exception: ReportedException,
    ) -> Optional[FuzzResult]:
        metadata = reported_exception.metadata
        if len(metadata) > 0 and isinstance(metadata[0], FuzzInputExceptionMetadata):
            fuzz_runs_count = reported_exception.execution_info["fuzz_runs"]
            assert isinstance(fuzz_runs_count, int)
            return FuzzResult(fuzz_runs_count)
        return None
