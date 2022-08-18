from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class TestCase:
    test_fn_name: str


@dataclass(frozen=True)
class TestSuite:
    test_path: Path
    test_cases: List[TestCase]
    setup_fn_name: Optional[str] = None

    def get_test_case_names(self) -> List[str]:
        return [tc.test_fn_name for tc in self.test_cases]
