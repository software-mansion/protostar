from dataclasses import dataclass
from typing import Optional

from typing_extensions import NotRequired, TypedDict


class CheatcodeNetworkConfig(TypedDict):
    wait_for_acceptance: NotRequired[bool]


@dataclass
class ValidatedCheatcodeNetworkConfig:
    @classmethod
    def from_dict(
        cls, config: Optional[CheatcodeNetworkConfig]
    ) -> "ValidatedCheatcodeNetworkConfig":
        if config is None:
            return cls()
        return cls(wait_for_acceptance=config.get("wait_for_acceptance", False))

    wait_for_acceptance: bool = False
