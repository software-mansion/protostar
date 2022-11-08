import pytest

from ..network_config import PredefinedNetwork
from .viewblock_block_explorer import ViewblockBlockExplorer

URL_PREFIX = "https://v2.viewblock.io/starknet"


@pytest.mark.parametrize(
    "network, tx_hash, result",
    [
        (
            "mainnet",
            999,
            f"{URL_PREFIX}/tx/0x00000000000000000000000000000000000000000000000000000000000003e7",
        ),
        (
            "testnet",
            999,
            f"{URL_PREFIX}/tx/0x00000000000000000000000000000000000000000000000000000000000003e7?network=goerli",
        ),
    ],
)
def test_creating_link_to_transaction(
    network: PredefinedNetwork, tx_hash: int, result: str
):
    explorer = ViewblockBlockExplorer(network=network)

    link = explorer.create_link_to_transaction(tx_hash)

    assert link == result


@pytest.mark.parametrize(
    "network, contract_address, result",
    [
        (
            "mainnet",
            999,
            f"{URL_PREFIX}/contract/0x00000000000000000000000000000000000000000000000000000000000003e7",
        ),
        (
            "testnet",
            999,
            f"{URL_PREFIX}/contract/0x00000000000000000000000000000000000000000000000000000000000003e7?network=goerli",
        ),
    ],
)
def test_creating_link_to_contract(
    network: PredefinedNetwork, contract_address: int, result: str
):
    explorer = ViewblockBlockExplorer(network=network)

    link = explorer.create_link_to_contract(contract_address)

    assert link == result


@pytest.mark.parametrize(
    "network, class_hash, result",
    [
        (
            "mainnet",
            999,
            f"{URL_PREFIX}/class/0x00000000000000000000000000000000000000000000000000000000000003e7",
        ),
        (
            "testnet",
            999,
            f"{URL_PREFIX}/class/0x00000000000000000000000000000000000000000000000000000000000003e7?network=goerli",
        ),
    ],
)
def test_creating_link_to_class(
    network: PredefinedNetwork, class_hash: int, result: str
):
    explorer = ViewblockBlockExplorer(network=network)

    link = explorer.create_link_to_class(class_hash)

    assert link == result
