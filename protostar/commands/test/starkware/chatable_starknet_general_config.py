from dataclasses import field
from pathlib import Path
from typing import List, Optional


import marshmallow_dataclass
from marshmallow import fields
from starkware.starknet.definitions.general_config import StarknetGeneralConfig

@marshmallow_dataclass.dataclass(frozen=True)
class CheatableStarknetGeneralConfig(StarknetGeneralConfig):
    cheatcodes_cairo_path: List[str] = field(default_factory=list)