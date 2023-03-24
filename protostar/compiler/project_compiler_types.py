from dataclasses import dataclass
from pathlib import Path
from typing import Union, List

ContractName = str
ContractSourcePath = Path
ContractIdentifier = Union[ContractName, ContractSourcePath]


@dataclass
class ProjectCompilerConfig:
    relative_cairo_path: List[Path]
    debugging_info_attached: bool = False
    hint_validation_disabled: bool = False
