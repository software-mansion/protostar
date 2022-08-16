from protostar.commands.test.test_collector_summary_formatter import (
    format_test_collector_summary,
)


def test_logging_collected_one_test_suite_and_one_test_case():
    result = format_test_collector_summary(
        test_case_count=1, test_suite_count=1, duration_in_sec=0
    )

    assert result.startswith("Collected 1 suite, and 1 test case (0.000 s)")


def test_logging_many_test_suites_and_many_test_cases():

    result = format_test_collector_summary(
        test_case_count=2, test_suite_count=4, duration_in_sec=1 / 3
    )

    assert result.startswith("Collected 4 suites, and 2 test cases (0.333 s)")
