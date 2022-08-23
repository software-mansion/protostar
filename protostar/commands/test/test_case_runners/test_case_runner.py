import time
from typing import Optional

from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputRecorder
from protostar.commands.test.test_results import (
    FailedTestCaseResult,
    PassedTestCaseResult,
    TestCaseResult,
    TestCaseResultDecorator,
)
from protostar.commands.test.test_suite import TestCase


class TestCaseRunner:
    def __init__(
        self,
        execution_environment: TestExecutionEnvironment,
        test_case: TestCase,
        output_recorder: OutputRecorder,
        test_case_result_decorator: Optional[TestCaseResultDecorator] = None,
    ) -> None:
        self._test_case = test_case
        self._execution_environment = execution_environment
        self._test_case_result_decorator = (
            test_case_result_decorator or TestCaseResultDecorator()
        )
        self._output_recorder = output_recorder

    async def run(self) -> TestCaseResult:
        timer = Timer()
        try:
            with timer:
                execution_result = await self._execution_environment.invoke(
                    self._test_case.test_fn_name
                )

            return self._test_case_result_decorator.decorate_passed(
                result=PassedTestCaseResult(
                    file_path=self._test_case.test_path,
                    test_case_name=self._test_case.test_fn_name,
                    execution_resources=execution_result.execution_resources,
                    execution_time=timer.elapsed,
                    captured_stdout=self._output_recorder.get_captures(),
                ),
                execution_result=execution_result,
            )
        except ReportedException as ex:
            return self._test_case_result_decorator.decorate_failed(
                result=FailedTestCaseResult(
                    file_path=self._test_case.test_path,
                    test_case_name=self._test_case.test_fn_name,
                    exception=ex,
                    execution_time=timer.elapsed,
                    captured_stdout=self._output_recorder.get_captures(),
                ),
                exception=ex,
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
