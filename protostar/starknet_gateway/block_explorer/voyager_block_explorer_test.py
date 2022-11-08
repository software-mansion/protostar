import pytest

from ..network_config import PredefinedNetwork
from .voyager_block_explorer import VoyagerBlockExplorer


@pytest.mark.parametrize(
    "network, domain",
    [
        ("mainnet", "https://voyager.online"),
        ("testnet", "https://goerli.voyager.online"),
    ],
)
def test_creating_link_to_transaction(network: PredefinedNetwork, domain: str):
    explorer = VoyagerBlockExplorer(network=network)

    link = explorer.create_link_to_transaction(999)

    assert (
        link
        == f"{domain}/tx/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )


@pytest.mark.parametrize(
    "network, domain",
    [
        ("mainnet", "https://voyager.online"),
        ("testnet", "https://goerli.voyager.online"),
    ],
)
def test_creating_link_to_contract(network: PredefinedNetwork, domain: str):
    explorer = VoyagerBlockExplorer(network=network)

    link = explorer.create_link_to_contract(999)

    assert (
        link
        == f"{domain}/contract/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )


@pytest.mark.parametrize(
    "network, domain",
    [
        ("mainnet", "https://voyager.online"),
        ("testnet", "https://goerli.voyager.online"),
    ],
)
def test_creating_link_to_class(network: PredefinedNetwork, domain: str):
    explorer = VoyagerBlockExplorer(network=network)

    link = explorer.create_link_to_class(999)

    assert (
        link
        == f"{domain}/class/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )
