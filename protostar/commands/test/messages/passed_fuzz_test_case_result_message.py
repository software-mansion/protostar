from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider

from protostar.testing import PassedFuzzTestCaseResult

from .formatters import (
    get_formatted_execution_time_human,
    get_formatted_execution_time_structured,
    get_formatted_file_path,
    get_formatted_stdout,
)


@dataclass
class PassedFuzzTestCaseResultMessage(StructuredMessage):
    passed_fuzz_test_case_result: PassedFuzzTestCaseResult

    def format_human(self, fmt: LogColorProvider) -> str:
        first_line_elements: list[str] = [f"[{fmt.colorize('GREEN', 'PASS')}]"]
        formatted_file_path = get_formatted_file_path(
            file_path=self.passed_fuzz_test_case_result.file_path,
            log_color_provider=fmt,
        )
        first_line_elements.append(
            f"{formatted_file_path} {self.passed_fuzz_test_case_result.test_case_name}"
        )

        info_items: list[str] = [
            get_formatted_execution_time_human(
                execution_time=self.passed_fuzz_test_case_result.execution_time,
                log_color_provider=fmt,
            )
        ]

        if self.passed_fuzz_test_case_result.fuzz_runs_count is not None:
            info_items.append(
                f"fuzz_runs={fmt.bold(self.passed_fuzz_test_case_result.fuzz_runs_count)}"
            )

        if self.passed_fuzz_test_case_result.execution_resources:
            if (
                self.passed_fuzz_test_case_result.execution_resources.estimated_gas
                is not None
            ):
                info_items.append(
                    f"gas={fmt.bold(self.passed_fuzz_test_case_result.execution_resources.estimated_gas)}"
                )
            if self.passed_fuzz_test_case_result.execution_resources.n_steps:
                info_items.append(
                    f"steps={fmt.bold(self.passed_fuzz_test_case_result.execution_resources.n_steps)}"
                )
            if self.passed_fuzz_test_case_result.execution_resources.n_memory_holes:
                formatted_n_memory_holes = fmt.bold(
                    self.passed_fuzz_test_case_result.execution_resources.n_memory_holes
                )
                info_items.append(f"memory_holes={formatted_n_memory_holes}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_elements.append(fmt.colorize("GRAY", f"({info})"))

        first_line = " ".join(first_line_elements)

        second_line_elements: list[str] = []
        if self.passed_fuzz_test_case_result.execution_resources:
            for (
                builtin_name,
                builtin_count,
            ) in (
                self.passed_fuzz_test_case_result.execution_resources.builtin_name_to_count_map.items()
            ):
                if builtin_count:
                    second_line_elements.append(
                        fmt.colorize(
                            "GRAY",
                            f"{builtin_name}={fmt.bold(builtin_count)}",
                        )
                    )

        stdout_elements = get_formatted_stdout(
            captured_stdout=self.passed_fuzz_test_case_result.captured_stdout,
            log_color_provider=fmt,
        )

        if len(second_line_elements) > 0 or len(stdout_elements) > 0:
            second_line_elements.insert(0, "      ")
            second_line = " ".join(second_line_elements)

            # To maintain consistent spacing
            to_join: list[str] = [first_line, second_line]
            if stdout_elements:
                to_join.append("".join(stdout_elements))
            return "\n".join(to_join)

        return first_line

    def format_dict(self) -> dict:
        result = {
            "message_type": "test_case_result",
            "test_type": "passed_fuzz_test_case",
            "test_suite_path": str(self.passed_fuzz_test_case_result.file_path),
            "test_case_name": self.passed_fuzz_test_case_result.test_case_name,
            "execution_time_in_seconds": get_formatted_execution_time_structured(
                self.passed_fuzz_test_case_result.execution_time
            ),
            # "stdout": str(self.passed_fuzz_test_case_result.captured_stdout),
        }
        if self.passed_fuzz_test_case_result.fuzz_runs_count:
            result["fuzz_runs"] = str(self.passed_fuzz_test_case_result.fuzz_runs_count)
        return result
