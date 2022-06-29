from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class TestSuite:
    test_path: Path
    test_case_names: List[str]
    setup_fn_name: Optional[str] = None
