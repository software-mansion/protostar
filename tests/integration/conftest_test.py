from pathlib import Path

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.io import log_color_provider
from protostar.starknet.cheatable_starknet_exceptions import ReportedException
from protostar.testing.test_results import FailedTestCaseResult
from tests.integration.conftest import (
    CairoTestCases,
    show_diff_between_cairo_test_cases,
)


def test_diff_between_test_cases():
    name_to_actual_test_case = {
        "foo": FailedTestCaseResult(
            test_case_name="foo",
            file_path=Path("./path"),
            exception=ReportedException(),
            captured_stdout={},
            execution_time=0,
        )
    }

    expected_cairo_test_cases = CairoTestCases(
        passed=set(["foo"]),
        failed=set(["bar"]),
        broken=set(),
        skipped=set(),
    )
    actual_cairo_test_cases = CairoTestCases(
        passed=set(),
        failed=set(["foo", "bar"]),
        broken=set(),
        skipped=set(),
    )

    diff = show_diff_between_cairo_test_cases(
        name_to_actual_test_case, expected_cairo_test_cases, actual_cairo_test_cases
    )

    assert "Expected 'foo' to be passed, got" in diff
    assert (
        format_test_result(name_to_actual_test_case["foo"]).format_human(
            log_color_provider
        )
        in diff
    )
