import pytest

from protostar.starknet_gateway.network_config import (
    NetworkConfig,
    UnknownStarkwareNetworkException,
)


def test_loading_starkware_networks():
    assert NetworkConfig("alpha-goerli").gateway_url is not None
    assert NetworkConfig("alpha-mainnet").gateway_url is not None


def test_testnet_block_explorer():
    assert (
        NetworkConfig("alpha-goerli").get_contract_explorer_url(999)
        == "https://goerli.voyager.online/contract/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )
