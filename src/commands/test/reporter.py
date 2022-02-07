from functools import reduce
from pathlib import Path
from typing import List, Union, Optional, Dict

from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.cases import PassedCase, FailedCase, BrokenTest
from src.commands.test.utils import TestSubject

CaseResult = Union[PassedCase, FailedCase, BrokenTest]


def print_stark_exception(exception: StarkException):
    indented_message = "\t" + exception.message.replace("\n", "\n\t")
    print("Error type:")
    print(f"\t{exception.code.name}")
    print("Error message:")
    print(indented_message)
    print("Error code:")
    print(f"\t{exception.code.value}")


class TestReporter:
    _collected_count: Optional[int]
    broken_tests: List[BrokenTest]
    failed_cases: List[FailedCase]
    passed_cases: List[PassedCase]
    failed_tests_by_subject: Dict[Path, List[FailedCase]]
    collected_subjects: List[TestSubject]
    tests_root: Path

    def __init__(self, tests_root: Path):
        self.broken_tests = []
        self.failed_cases = []
        self.passed_cases = []
        self.failed_tests_by_subject = {}
        self.collected_subjects = []
        self._collected_count = None
        self.tests_root = tests_root

    def report(self, subject: TestSubject, case_result: CaseResult):
        symbol = None
        if isinstance(case_result, PassedCase):
            symbol = "."
            self.passed_cases.append(case_result)
        if isinstance(case_result, FailedCase):
            symbol = "F"
            self.failed_cases.append(case_result)
            try:
                self.failed_tests_by_subject[subject.test_path].append(case_result)
            except KeyError:
                self.failed_tests_by_subject[subject.test_path] = [case_result]

        if isinstance(case_result, BrokenTest):
            symbol = "!"
            self.broken_tests.append(case_result)
        assert symbol, "Unrecognised case result!"

        print(symbol, end="")

    @staticmethod
    def file_entry(file_name: str):
        print(f"\n{file_name.replace('.cairo', '')}: ", end="")

    @staticmethod
    def report_collection_error():
        print("!!!!!!!!!! TEST COLLECTION ERROR !!!!!!!!!!")

    def report_summary(self):
        if not self.collected_count:
            return

        failed_tests_amt = len(self.failed_cases)
        succeeded_tests_amt = len(self.passed_cases)
        broken_tests_amt = len(self.broken_tests)

        ran_tests = succeeded_tests_amt + failed_tests_amt

        print("\n----- TEST SUMMARY ------")
        if failed_tests_amt:
            print(f"{failed_tests_amt} failed, ", end="")
        if broken_tests_amt:
            print(f"{broken_tests_amt} failed to run, ", end="")

        print(f"{succeeded_tests_amt} passed")
        print(f"Ran {ran_tests} out of {self.collected_count} total tests")

        self._report_failures()

    def _report_failures(self):
        if self.failed_cases:
            print("\n----- FAILURES ------")
            for test_path, failed_cases in self.failed_tests_by_subject.items():

                for failed_case in failed_cases:
                    print(
                        f"{test_path.resolve().relative_to(self.tests_root.resolve())}::{failed_case.function_name}"
                    )
                    print_stark_exception(failed_case.exception)
        if self.broken_tests:
            print("\n----- BROKEN TESTS ------")
            for broken_subject in self.broken_tests:
                print(broken_subject.file_path.resolve().relative_to(self.tests_root.resolve()))
                print_stark_exception(broken_subject.exception)

    def report_collected(self, test_subjects: List[TestSubject]):
        self.collected_subjects = test_subjects

        if self.collected_count:
            print(f"Collected {self.collected_count} items")
        else:
            print("No cases found")

    @property
    def collected_count(self) -> int:
        if self._collected_count is None:
            self._collected_count = reduce(
                lambda x, y: x + y,
                [len(subject.test_functions) for subject in self.collected_subjects],
                0,
            )
        return self._collected_count
