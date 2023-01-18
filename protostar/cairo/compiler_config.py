from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CompilerConfig:
    include_paths: List[str]
    disable_hint_validation: bool
