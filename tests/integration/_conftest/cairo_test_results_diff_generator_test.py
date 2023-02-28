from pathlib import Path

from protostar.commands.cairo0.test import format_test_result
from protostar.io import log_color_provider
from protostar.starknet.cheatable_starknet_exceptions import ReportedException
from protostar.testing.test_results import FailedTestCaseResult

from .cairo_test_results_data import CairoTestResultsData
from .cairo_test_results_diff_generator import CairoTestCasesDiffGenerator


def test_diff_between_test_cases():
    test_case_name_to_result = {
        "foo": FailedTestCaseResult(
            test_case_name="foo",
            file_path=Path("./path"),
            exception=ReportedException(),
            captured_stdout={},
            execution_time=0,
        )
    }
    diff_generator = CairoTestCasesDiffGenerator(
        test_case_name_to_result=test_case_name_to_result
    )
    expected_test_results_data = CairoTestResultsData(
        passed=set(["foo"]),
        failed=set(["bar"]),
        broken=set(),
        skipped=set(),
    )
    actual_test_results_data = CairoTestResultsData(
        passed=set(),
        failed=set(["foo", "bar"]),
        broken=set(),
        skipped=set(),
    )

    diff = diff_generator.execute(
        expected_test_results_data=expected_test_results_data,
        actual_test_results_data=actual_test_results_data,
    )

    assert "Expected 'foo' to be passed, got" in diff
    assert (
        format_test_result(test_case_name_to_result["foo"]).format_human(
            log_color_provider
        )
        in diff
    )
