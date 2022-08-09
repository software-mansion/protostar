from pathlib import Path
from typing import Callable, Dict, List

from protostar.commands.test.test_environment_exceptions import ExceptionMetadata
from protostar.commands.test.test_output_recorder import OutputName, format_output_name
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG
from protostar.utils.log_color_provider import LogColorProvider

from .test_cases import (
    BrokenTestSuiteResult,
    FailedFuzzTestCaseResult,
    FailedTestCaseResult,
    PassedFuzzTestCaseResult,
    PassedTestCaseResult,
    TestResult,
    UnexpectedExceptionTestSuiteResult,
)

LogCallback = Callable[[str], None]


class TestResultFormatter:
    def __init__(
        self,
        log_color_provider: LogColorProvider,
    ) -> None:
        super().__init__()
        self._log_color_provider = log_color_provider

    # pylint: disable=too-many-return-statements
    def format(self, test_result: TestResult) -> str:
        if isinstance(test_result, PassedFuzzTestCaseResult):
            return self._format_passed_fuzz_test_case_result(test_result)
        if isinstance(test_result, FailedFuzzTestCaseResult):
            return self._format_failed_fuzz_test_case_result(test_result)
        if isinstance(test_result, PassedTestCaseResult):
            return self._format_passed_test_case_result(test_result)
        if isinstance(test_result, FailedTestCaseResult):
            return self._format_failed_test_case_result(test_result)
        if isinstance(test_result, UnexpectedExceptionTestSuiteResult):
            return self._format_unexpected_exception_test_suite_result(test_result)
        if isinstance(test_result, BrokenTestSuiteResult):
            return self._format_broken_test_suite_result(test_result)
        return ""

    def _format_passed_test_case_result(
        self, passed_test_case_result: PassedTestCaseResult
    ) -> str:
        return self._format_passed_fuzz_test_case_result(
            PassedFuzzTestCaseResult(
                captured_stdout=passed_test_case_result.captured_stdout,
                execution_resources=passed_test_case_result.execution_resources,
                file_path=passed_test_case_result.file_path,
                execution_time=passed_test_case_result.execution_time,
                test_case_name=passed_test_case_result.test_case_name,
                fuzz_runs_count=None,
            )
        )

    def _format_failed_test_case_result(
        self, failed_test_case_result: FailedTestCaseResult
    ) -> str:
        result: List[str] = []
        first_line_items: List[str] = []

        first_line_items.append(f"[{self._log_color_provider.colorize('RED', 'FAIL')}]")
        formatted_file_path = self._get_formatted_file_path(
            failed_test_case_result.file_path
        )
        first_line_items.append(
            f"{formatted_file_path} {failed_test_case_result.test_case_name}"
        )

        info_items = []

        info_items.append(
            self._get_formatted_execution_time(failed_test_case_result.execution_time)
        )

        for key, value in failed_test_case_result.exception.execution_info.items():
            info_items.append(f"{key}={self._log_color_provider.bold(value)}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_items.append(
                self._log_color_provider.colorize("GRAY", f"({info})")
            )

        result.append(" ".join(first_line_items))

        result.append("\n")
        result.append(str(failed_test_case_result.exception))
        result.append("\n")

        for metadata in failed_test_case_result.exception.metadata:
            result.append(self._get_formatted_metadata(metadata))
            result.append("\n")

        result.extend(
            self._get_formatted_stdout(failed_test_case_result.captured_stdout)
        )

        return "".join(result)

    def _format_passed_fuzz_test_case_result(
        self, passed_fuzz_test_case_result: PassedFuzzTestCaseResult
    ) -> str:
        first_line_elements: List[str] = []
        first_line_elements.append(
            f"[{self._log_color_provider.colorize('GREEN', 'PASS')}]"
        )
        formatted_file_path = self._get_formatted_file_path(
            passed_fuzz_test_case_result.file_path
        )
        first_line_elements.append(
            f"{formatted_file_path} {passed_fuzz_test_case_result.test_case_name}"
        )

        info_items: List[str] = []

        info_items.append(
            self._get_formatted_execution_time(
                passed_fuzz_test_case_result.execution_time
            )
        )

        if passed_fuzz_test_case_result.fuzz_runs_count is not None:
            info_items.append(
                f"fuzz_runs={self._log_color_provider.bold(passed_fuzz_test_case_result.fuzz_runs_count)}"
            )

        if passed_fuzz_test_case_result.execution_resources:
            if passed_fuzz_test_case_result.execution_resources.n_steps:
                info_items.append(
                    f"steps={self._log_color_provider.bold(passed_fuzz_test_case_result.execution_resources.n_steps)}"
                )
            if passed_fuzz_test_case_result.execution_resources.n_memory_holes:
                formatted_n_memory_holes = self._log_color_provider.bold(
                    passed_fuzz_test_case_result.execution_resources.n_memory_holes
                )
                info_items.append(f"memory_holes={formatted_n_memory_holes}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_elements.append(
                self._log_color_provider.colorize("GRAY", f"({info})")
            )

        first_line = " ".join(first_line_elements)

        second_line_elements: List[str] = []
        if passed_fuzz_test_case_result.execution_resources:
            for (
                builtin_name,
                builtin_count,
            ) in (
                passed_fuzz_test_case_result.execution_resources.builtin_name_to_count_map.items()
            ):
                if builtin_count:
                    second_line_elements.append(
                        self._log_color_provider.colorize(
                            "GRAY",
                            f"{builtin_name}={self._log_color_provider.bold(builtin_count)}",
                        )
                    )

        stdout_elements = self._get_formatted_stdout(
            passed_fuzz_test_case_result.captured_stdout
        )

        if len(second_line_elements) > 0 or len(stdout_elements) > 0:
            second_line_elements.insert(0, "      ")
            second_line = " ".join(second_line_elements)

            # To maintain consistent spacing
            to_join: List[str] = [first_line, second_line]
            if stdout_elements:
                to_join.append("".join(stdout_elements))
            return "\n".join(to_join)

        return first_line

    def _format_failed_fuzz_test_case_result(self, failed_fuzz_test_case_result) -> str:
        return self._format_failed_test_case_result(failed_fuzz_test_case_result)

    def _format_broken_test_suite_result(self, broken_test_suite_result) -> str:
        first_line: List[str] = []
        first_line.append(f"[{self._log_color_provider.colorize('RED', 'BROKEN')}]")
        first_line.append(
            f"{self._get_formatted_file_path(broken_test_suite_result.file_path)}"
        )
        result = [" ".join(first_line)]
        result.append(str(broken_test_suite_result.exception))
        return "\n".join(result)

    def _format_unexpected_exception_test_suite_result(
        self, unexpected_exception_test_suite_result: UnexpectedExceptionTestSuiteResult
    ) -> str:
        lines: List[str] = []
        main_line: List[str] = []
        main_line.append(
            f"[{self._log_color_provider.colorize('RED', 'UNEXPECTED_EXCEPTION')}]"
        )
        main_line.append(
            self._get_formatted_file_path(
                unexpected_exception_test_suite_result.file_path
            )
        )
        lines.append(" ".join(main_line))

        if unexpected_exception_test_suite_result.traceback:
            lines.append(unexpected_exception_test_suite_result.traceback)

        lines.append(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        lines.append(str(unexpected_exception_test_suite_result.exception))
        return "\n".join(lines)

    def _get_formatted_file_path(self, file_path: Path) -> str:
        return self._log_color_provider.colorize("GRAY", str(file_path))

    def _get_formatted_execution_time(self, execution_time: float) -> str:
        return f"time={self._log_color_provider.bold(f'{execution_time:.2f}')}s"

    def _get_formatted_stdout(
        self, captured_stdout: Dict[OutputName, str]
    ) -> List[str]:
        result: List[str] = []

        if len(captured_stdout) == 0 or all(
            len(val) == 0 for _, val in captured_stdout.items()
        ):
            return []

        result.append(
            f"\n[{self._log_color_provider.colorize('CYAN', 'captured stdout')}]:\n"
        )

        for name, value in captured_stdout.items():
            if value:
                result.append(
                    f"[{format_output_name(name)}]:\n{self._log_color_provider.colorize('GRAY', value)}\n"
                )

        return result

    @staticmethod
    def _get_formatted_metadata(metadata: ExceptionMetadata) -> str:
        return f"[{metadata.name}]:\n{metadata.format()}"
