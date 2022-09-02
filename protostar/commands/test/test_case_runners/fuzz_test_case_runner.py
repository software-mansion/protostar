from typing import Optional

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
    FuzzTestExecutionResult,
)
from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner
from protostar.commands.test.test_environment_exceptions import (
    ReportedException,
    BreakingReportedException,
)
from protostar.commands.test.test_results import (
    FailedFuzzTestCaseResult,
    FailedTestCaseResult,
    FuzzResult,
    PassedFuzzTestCaseResult,
    BrokenTestCaseResult,
    BrokenFuzzTestCaseResult,
)


class FuzzTestCaseRunner(TestCaseRunner[FuzzTestExecutionResult]):
    def __init__(
        self, fuzz_test_execution_environment: FuzzTestExecutionEnvironment, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._fuzz_test_execution_environment = fuzz_test_execution_environment

    async def _run_test_case(self) -> FuzzTestExecutionResult:
        return await self._fuzz_test_execution_environment.invoke(
            self._test_case.test_fn_name
        )

    def _map_execution_result_to_passed_test_result(
        self,
        execution_result: FuzzTestExecutionResult,
        execution_metadata: TestCaseRunner.ExecutionMetadata,
    ) -> PassedFuzzTestCaseResult:
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

    def _map_reported_exception_to_broken_test_result(
        self,
        reported_exception: BreakingReportedException,
        execution_metadata: TestCaseRunner.ExecutionMetadata,
    ) -> BrokenTestCaseResult:
        broken_test_case_result = super()._map_reported_exception_to_broken_test_result(
            reported_exception, execution_metadata
        )
        fuzz_result = self._map_reported_exception_to_fuzz_result(reported_exception)
        if fuzz_result:
            return BrokenFuzzTestCaseResult.from_broken_test_case_result(
                broken_test_case_result,
                fuzz_result,
            )
        return BrokenFuzzTestCaseResult.from_broken_test_case_result(
            broken_test_case_result,
            fuzz_result=None,
        )

    @staticmethod
    def _map_reported_exception_to_fuzz_result(
        reported_exception: ReportedException,
    ) -> Optional[FuzzResult]:
        fuzz_input = reported_exception.get_metadata_by_type(FuzzInputExceptionMetadata)
        if fuzz_input:
            fuzz_runs_count = reported_exception.execution_info["fuzz_runs"]
            assert isinstance(fuzz_runs_count, int)
            return FuzzResult(fuzz_runs_count=fuzz_runs_count)

        return None
