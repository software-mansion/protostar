def format_test_collector_summary(
    test_case_count: int, test_suite_count: int, duration_in_sec: float
):
    n_test_suites = _format_test_suites_info(test_suite_count)
    n_test_cases = _format_test_case_info(test_case_count)
    duration = _format_duration(duration_in_sec)
    return f"Collected {n_test_suites}, and {n_test_cases} ({duration})"


def _format_test_suites_info(test_suite_count: int) -> str:
    if test_suite_count == 1:
        return "1 suite"
    return f"{test_suite_count} suites"


def _format_test_case_info(test_case_count: int) -> str:
    if test_case_count == 1:
        return "1 test case"
    return f"{test_case_count} test cases"


def _format_duration(duration_in_sec: float) -> str:
    return f"{duration_in_sec:.3f} s"
