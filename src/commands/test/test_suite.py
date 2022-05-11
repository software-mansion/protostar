from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.utils.starknet_compilation import StarknetCompiler


@dataclass
class TestSuite:
    TestFunction = StarknetCompiler.AbiElement

    test_path: Path
    test_functions: List["TestSuite.TestFunction"]
