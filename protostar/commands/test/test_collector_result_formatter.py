from logging import Logger
from typing import List

from .test_collector import TestCollector
from .test_result_cli_formatter_visitor import TestResultCLIFormatter


class TestCollectorCLIFormatter:
    def __init__(
        self,
        logger: Logger,
        test_result_cli_formatter_visitor: TestResultCLIFormatter,
    ) -> None:
        self._logger = logger
        self._test_result_cli_formatter_visitor = test_result_cli_formatter_visitor

    def log(self, test_collector_result: TestCollector.Result):
        for broken_test_suite in test_collector_result.broken_test_suites:
            broken_test_suite.accept(self._test_result_cli_formatter_visitor)
        if test_collector_result.test_cases_count:
            result: List[str] = ["Collected"]
            suites_count = len(test_collector_result.test_suites)
            if suites_count == 1:
                result.append("1 suite,")
            else:
                result.append(f"{suites_count} suites,")

            result.append("and")
            if test_collector_result.test_cases_count == 1:
                result.append("1 test case")
            else:
                result.append(f"{test_collector_result.test_cases_count} test cases")

            result.append(f"({test_collector_result.duration:.3f} s)")

            self._logger.info(" ".join(result))
        else:
            self._logger.warning("No test cases found")
