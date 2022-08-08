from typing_extensions import TypedDict


class NetworkConfig(TypedDict):
    wait_for_acceptance: bool


def get_default_network_config() -> NetworkConfig:
    return NetworkConfig(wait_for_acceptance=False)
