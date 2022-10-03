import os.path
from pathlib import Path
from typing import List, Optional

from protostar.testing import TestingSummary
from protostar.testing.test_results import (
    FailedTestCaseResult,
    BrokenTestCaseResult,
    BrokenTestSuiteResult,
)

from protostar.self.cache_io import CacheIO


class TestCommandCache:
    def __init__(self, cache_path: Path):
        self.cache_io = CacheIO(str(cache_path))

    def obtain_targets(self, targets: List[str], last_failed=False) -> List[str]:
        if not last_failed:
            return targets
        if targets_from_cache := self.read_targets_from_cache(targets):
            targets = targets_from_cache
            print("running previously failed tests:", targets)
        return targets

    def read_targets_from_cache(self, targets) -> Optional[list]:
        previous_results = self.cache_io.read("test_results")
        if not previous_results:
            return None
        previously_failed_tests = previous_results["failed_tests"]
        if not previously_failed_tests:
            return None
        # consider only the tests that are in one of the targets
        new_targets = []
        for failed_test in previously_failed_tests:
            is_in_targets = False
            for target in targets:
                if (
                    Path(os.path.abspath(target))
                    in Path(os.path.abspath(failed_test[0])).parents
                ):
                    is_in_targets = True
                    break
            if is_in_targets:
                new_targets.append(f"{failed_test[0]}::{failed_test[1]}")

        return new_targets

    def write_failed_tests_to_cache(self, summary: TestingSummary):
        failed_test_cases = []
        for failed_test in summary.failed + summary.broken + summary.broken_suites:
            if isinstance(failed_test, (BrokenTestCaseResult, FailedTestCaseResult)):
                failed_test_cases.append(
                    (str(failed_test.file_path), failed_test.test_case_name)
                )
            if isinstance(failed_test, BrokenTestSuiteResult):
                for test_name in failed_test.test_case_names:
                    failed_test_cases.append((str(failed_test.file_path), test_name))
        self.cache_io.write(
            "test_results",
            {"failed_tests": failed_test_cases},
        )
