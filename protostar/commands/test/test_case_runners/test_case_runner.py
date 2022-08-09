import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionResult,
)
from protostar.commands.test.test_cases import (
    FailedTestCaseResult,
    PassedTestCaseResult,
    TestResult,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputRecorder
from protostar.commands.test.test_suite import TestSuite

TExecutionResult = TypeVar("TExecutionResult", bound=TestExecutionResult)


class TestCaseRunner(Generic[TExecutionResult]):
    @dataclass
    class Dependencies:
        test_suite: TestSuite
        output_recorder: OutputRecorder

    @dataclass
    class ExecutionMetadata:
        test_case_name: str
        execution_time: float

    def __init__(self, dependencies: Dependencies) -> None:
        super().__init__()
        self._test_suite = dependencies.test_suite
        self._output_recorder = dependencies.output_recorder

    async def run(self, test_case_name: str) -> TestResult:
        start_time = time.perf_counter()
        try:
            execution_result = await self._run_test_case(test_case_name)
            execution_time = time.perf_counter() - start_time
            return self._map_execution_result_to_passed_test_result(
                execution_result,
                TestCaseRunner.ExecutionMetadata(test_case_name, execution_time),
            )
        except ReportedException as ex:
            execution_time = time.perf_counter() - start_time
            return self._map_reported_exception_to_failed_test_result(
                ex,
                TestCaseRunner.ExecutionMetadata(test_case_name, execution_time),
            )

    @abstractmethod
    async def _run_test_case(self, test_case_name: str) -> TExecutionResult:
        ...

    def _map_execution_result_to_passed_test_result(
        self, execution_result: TExecutionResult, execution_metadata: ExecutionMetadata
    ) -> PassedTestCaseResult:
        return PassedTestCaseResult(
            file_path=self._test_suite.test_path,
            test_case_name=execution_metadata.test_case_name,
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
            file_path=self._test_suite.test_path,
            test_case_name=execution_metadata.test_case_name,
            exception=reported_exception,
            execution_time=execution_metadata.execution_time,
            captured_stdout=self._output_recorder.get_captures(),
        )
