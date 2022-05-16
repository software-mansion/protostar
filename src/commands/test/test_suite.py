from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class TestSuite:
    test_path: Path
    test_case_names: List[str]
