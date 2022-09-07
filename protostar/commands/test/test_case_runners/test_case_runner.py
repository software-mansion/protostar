from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionResult,
)
from protostar.commands.test.stopwatch import Stopwatch
from protostar.commands.test.test_environment_exceptions import (
    ReportedException,
    BreakingReportedException,
)
from protostar.commands.test.test_output_recorder import OutputRecorder
from protostar.commands.test.test_results import (
    FailedTestCaseResult,
    PassedTestCaseResult,
    BrokenTestCaseResult,
    TestCaseResult,
)
from protostar.commands.test.test_suite import TestCase

TExecutionResult = TypeVar("TExecutionResult", bound=TestExecutionResult)


class TestCaseRunner(Generic[TExecutionResult]):
    @dataclass
    class ExecutionMetadata:
        execution_time: float

    def __init__(
        self,
        test_case: TestCase,
        output_recorder: OutputRecorder,
        stopwatch: Stopwatch,
    ) -> None:
        self._test_case = test_case
        self._output_recorder = output_recorder
        self._stopwatch = stopwatch

    async def run(self) -> TestCaseResult:
        try:
            with self._stopwatch.lap(self._test_case.test_fn_name):
                execution_result = await self._run_test_case()

            return self._map_execution_result_to_passed_test_result(
                execution_result,
                TestCaseRunner.ExecutionMetadata(self._stopwatch.total_elapsed),
            )
        except BreakingReportedException as ex:
            return self._map_breaking_reported_exception_to_broken_test_result(
                ex,
                TestCaseRunner.ExecutionMetadata(self._stopwatch.total_elapsed),
            )
        except ReportedException as ex:
            return self._map_reported_exception_to_failed_test_result(
                ex,
                TestCaseRunner.ExecutionMetadata(self._stopwatch.total_elapsed),
            )

    @abstractmethod
    async def _run_test_case(self) -> TExecutionResult:
        ...

    def _map_execution_result_to_passed_test_result(
        self, execution_result: TExecutionResult, execution_metadata: ExecutionMetadata
    ) -> PassedTestCaseResult:
        return PassedTestCaseResult(
            file_path=self._test_case.test_path,
            test_case_name=self._test_case.test_fn_name,
            execution_resources=execution_result.execution_resources,
            execution_time=execution_metadata.execution_time,
            captured_stdout=self._output_recorder.get_captures(),
        )

    def _map_reported_exception_to_failed_test_result(
        self,
        reported_exception: ReportedException,
        execution_metadata: ExecutionMetadata,
    ) -> FailedTestCaseResult:
        return FailedTestCaseResult(
            file_path=self._test_case.test_path,
            test_case_name=self._test_case.test_fn_name,
            exception=reported_exception,
            execution_time=execution_metadata.execution_time,
            captured_stdout=self._output_recorder.get_captures(),
        )

    def _map_breaking_reported_exception_to_broken_test_result(
        self,
        reported_exception: BreakingReportedException,
        execution_metadata: ExecutionMetadata,
    ) -> BrokenTestCaseResult:
        return BrokenTestCaseResult(
            file_path=self._test_case.test_path,
            test_case_name=self._test_case.test_fn_name,
            exception=reported_exception,
            execution_time=execution_metadata.execution_time,
            captured_stdout=self._output_recorder.get_captures(),
        )
