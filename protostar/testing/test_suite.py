from pathlib import Path
from typing import List, Optional
from typing_extensions import Self

from protostar.cairo.cairo_function_executor import Offset


class TestCase:
    def __init__(
        self, test_path: Path, test_fn_name: str, setup_fn_name: Optional[str] = None
    ):
        self.test_path = test_path
        self.test_fn_name = test_fn_name
        self.setup_fn_name = setup_fn_name


class TestSuite:
    def __init__(
        self,
        test_path: Path,
        test_cases: List[TestCase],
        setup_fn_name: Optional[str] = None,
    ):
        self.test_path = test_path
        self.test_cases = test_cases
        self.setup_fn_name = setup_fn_name

    def collect_test_case_names(self) -> List[str]:
        return [tc.test_fn_name for tc in self.test_cases]

    def add_offsets_to_cases(self, offset_map: dict[str, Offset]):
        self.test_cases = [
            TestCaseWithOffsets(
                test_path=case.test_path,
                test_fn_name=case.test_fn_name,
                test_fn_offset=offset_map.get(case.test_fn_name),
                setup_fn_name=case.setup_fn_name,
                setup_fn_offset=offset_map.get(case.test_fn_name),
            )
            for case in self.test_cases
        ]


class Cairo1TestSuite(TestSuite):
    def __init__(
        self,
        test_path: Path,
        test_cases: List[TestCase],
        sierra_output: str,
        setup_fn_name: Optional[str] = None,
    ):
        super().__init__(test_path, test_cases, setup_fn_name)
        self.sierra_output = sierra_output

    @classmethod
    def from_test_suite(cls, test_suite: TestSuite, sierra_output: str) -> Self:
        return cls(
            test_path=test_suite.test_path,
            test_cases=test_suite.test_cases,
            setup_fn_name=test_suite.setup_fn_name,
            sierra_output=sierra_output,
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
