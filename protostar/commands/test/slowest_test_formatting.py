from typing import List, Union
from protostar.commands.test.test_cases import FailedTestCase, PassedTestCase
from protostar.commands.test.testing_summary import TestingSummary
from protostar.utils.log_color_provider import log_color_provider


def _get_slowest_list(
    failed_and_passed_list: List[Union[PassedTestCase, FailedTestCase]],
    count: int,
) -> List[Union[PassedTestCase, FailedTestCase]]:
    lst = sorted(failed_and_passed_list, key=lambda x: x.execution_time, reverse=True)
    return lst[: min(count, len(lst))]


def get_formatted_slow_tests(testing_summary: TestingSummary, count: int) -> str:

    slowest = _get_slowest_list(testing_summary.failed + testing_summary.passed, count)

    rows: List[List[str]] = []
    for i, test_case in enumerate(slowest, 1):
        row: List[str] = []
        row.append(
            f"[{log_color_provider.colorize('RED' if isinstance(test_case, FailedTestCase) else 'GREEN', str(i))}]  "
        )

        row.append(f"{log_color_provider.colorize('GRAY', test_case.file_path)}")
        row.append(test_case.test_case_name)
        row.append(f"{test_case.execution_time:.2f} s")

        rows.append(row)

    widths = [max(map(len, col)) for col in zip(*rows)]
    return "\n".join(
        "  ".join((val.ljust(width) for val, width in zip(row, widths))) for row in rows
    )
