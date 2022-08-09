from dataclasses import dataclass
from typing_extensions import TypedDict, NotRequired


class CheatcodeNetworkConfig(TypedDict):
    wait_for_acceptance: NotRequired[bool]


@dataclass
class ValidatedCheatcodeNetworkConfig:
    @classmethod
    def from_dict(cls, config: CheatcodeNetworkConfig):
        return cls(wait_for_acceptance=config.get("wait_for_acceptance", False))

    wait_for_acceptance: bool = False
