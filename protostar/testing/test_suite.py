from pathlib import Path
from typing import List, Optional, Union
from typing_extensions import Self

from protostar.cairo.cairo_function_executor import Offset


class TestCase:
    def __init__(
        self, test_path: Path, test_fn_name: str, setup_fn_name: Optional[str] = None
    ):
        self.test_path = test_path
        self.test_fn_name = test_fn_name
        self.setup_fn_name = setup_fn_name

    def __eq__(self, other: Self) -> bool:
        return (
            other.test_path == self.test_path
            and other.test_fn_name == self.test_fn_name
            and other.setup_fn_name == self.setup_fn_name
        )


class TestCaseWithOffsets(TestCase):
    def __init__(
        self,
        test_path: Path,
        test_fn_name: str,
        test_fn_offset: int,
        setup_fn_name: Optional[str] = None,
        setup_fn_offset: Optional[int] = None,
    ):
        super().__init__(test_path, test_fn_name, setup_fn_name)
        self.test_fn_offset = test_fn_offset
        self.setup_fn_offset = setup_fn_offset


TestCases = Union[List[TestCase], List[TestCaseWithOffsets]]


class TestSuite:
    def __init__(
        self,
        test_path: Path,
        test_cases: TestCases,
        setup_fn_name: Optional[str] = None,
    ):
        self.test_path = test_path
        self.test_cases = test_cases
        self.setup_fn_name = setup_fn_name

    def collect_test_case_names(self) -> List[str]:
        return [tc.test_fn_name for tc in self.test_cases]


class Cairo1TestSuite(TestSuite):
    def __init__(
        self,
        test_path: Path,
        test_cases: TestCases,
        sierra_output: str,
        setup_fn_name: Optional[str] = None,
    ):
        super().__init__(test_path, [], setup_fn_name)
        self.test_cases = test_cases
        self.sierra_output = sierra_output

    @classmethod
    def from_test_suite(cls, test_suite: TestSuite, sierra_output: str) -> Self:
        return cls(
            test_path=test_suite.test_path,
            test_cases=test_suite.test_cases,
            setup_fn_name=test_suite.setup_fn_name,
            sierra_output=sierra_output,
        )

    def add_offsets_to_cases(self, offset_map: dict[str, Offset]):
        for test_case in self.test_cases:
            assert isinstance(
                test_case, TestCase
            ), f"Test case {test_case.test_fn_name} is not a plain test case!"

        mapped_cases = [
            self._convert_to_case_with_offsets(test_case=case, offset_map=offset_map)
            for case in self.test_cases
        ]
        self.test_cases.extend(mapped_cases)

    def _convert_to_case_with_offsets(
        self, test_case: TestCase, offset_map: dict[str, Offset]
    ) -> TestCaseWithOffsets:
        test_fn_offset = offset_map.get(test_case.test_fn_name)
        if not test_fn_offset:
            raise KeyError(
                f"No code offset found for test function: {test_case.test_fn_name}"
            )

        return TestCaseWithOffsets(
            test_path=test_case.test_path,
            test_fn_name=test_case.test_fn_name,
            test_fn_offset=test_fn_offset,
            setup_fn_name=test_case.setup_fn_name,
            setup_fn_offset=offset_map.get(test_case.test_fn_name),
        )
