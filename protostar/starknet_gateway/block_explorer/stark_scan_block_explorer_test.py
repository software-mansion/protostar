import pytest

from ..network_config import PredefinedNetwork
from .stark_scan_block_explorer import StarkScanBlockExplorer

MAINNET_DOMAIN = "https://starkscan.co"
TESTNET_DOMAIN = "https://testnet.starkscan.co"


@pytest.mark.parametrize(
    "network, domain",
    [
        ("mainnet", MAINNET_DOMAIN),
        ("testnet", TESTNET_DOMAIN),
    ],
)
def test_creating_link_to_transaction(network: PredefinedNetwork, domain: str):
    explorer = StarkScanBlockExplorer(network=network)

    link = explorer.create_link_to_transaction(999)

    assert (
        link
        == f"{domain}/tx/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )


@pytest.mark.parametrize(
    "network, domain",
    [
        ("mainnet", MAINNET_DOMAIN),
        ("testnet", TESTNET_DOMAIN),
    ],
)
def test_creating_link_to_contract(network: PredefinedNetwork, domain: str):
    explorer = StarkScanBlockExplorer(network=network)

    link = explorer.create_link_to_contract(999)

    assert (
        link
        == f"{domain}/contract/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )


@pytest.mark.parametrize(
    "network, domain",
    [
        ("mainnet", MAINNET_DOMAIN),
        ("testnet", TESTNET_DOMAIN),
    ],
)
def test_creating_link_to_class(network: PredefinedNetwork, domain: str):
    explorer = StarkScanBlockExplorer(network=network)

    link = explorer.create_link_to_class(999)

    assert (
        link
        == f"{domain}/class/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )
