from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.utils.starknet_compilation import StarknetCompiler


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """

    test_path: Path
    test_functions: List[StarknetCompiler.AbiElement]
