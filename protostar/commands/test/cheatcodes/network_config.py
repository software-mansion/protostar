from typing_extensions import TypedDict


class CheatcodeNetworkConfig(TypedDict):
    wait_for_acceptance: bool


def get_default_network_config() -> CheatcodeNetworkConfig:
    return CheatcodeNetworkConfig(wait_for_acceptance=False)
