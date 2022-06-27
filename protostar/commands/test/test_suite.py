from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)


@dataclass(frozen=True)
class TestSuite:
    test_path: Path
    # preprocessed_contract: StarknetPreprocessedProgram
    test_case_names: List[str]
    setup_fn_name: Optional[str] = None
