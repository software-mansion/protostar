# pylint: disable=too-many-ancestors
from dataclasses import field
from typing import List


import marshmallow_dataclass
from starkware.starknet.definitions.general_config import StarknetGeneralConfig


@marshmallow_dataclass.dataclass(frozen=True)
class CheatableStarknetGeneralConfig(StarknetGeneralConfig):
    cheatcodes_cairo_path: List[str] = field(default_factory=list)
