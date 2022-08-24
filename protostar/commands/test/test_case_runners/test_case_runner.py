import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionResult,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputRecorder
from protostar.commands.test.test_results import (
    FailedTestCaseResult,
    PassedTestCaseResult,
    TestCaseResult,
)
from protostar.commands.test.test_suite import TestCase

TExecutionResult = TypeVar("TExecutionResult", bound=TestExecutionResult)


class TestCaseRunner(Generic[TExecutionResult]):
    @dataclass
    class ExecutionMetadata:
        execution_time: float

    def __init__(self, test_case: TestCase, output_recorder: OutputRecorder) -> None:
        self._test_case = test_case
        self._output_recorder = output_recorder

    async def run(self) -> TestCaseResult:
        timer = Timer()
        try:
            with timer:
                execution_result = await self._run_test_case()

            return self._map_execution_result_to_passed_test_result(
                execution_result,
                TestCaseRunner.ExecutionMetadata(timer.elapsed),
            )
        except ReportedException as ex:
            return self._map_reported_exception_to_failed_test_result(
                ex,
                TestCaseRunner.ExecutionMetadata(timer.elapsed),
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


class Timer:
    def __init__(self):
        self._start_time = None
        self._end_time = None

    def __enter__(self):
        self._start_time = time.perf_counter()
        self._end_time = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.perf_counter()

    @property
    def elapsed(self) -> float:
        assert self._start_time is not None and self._end_time is not None
        return self._end_time - self._start_time
