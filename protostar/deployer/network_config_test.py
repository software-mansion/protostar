import pytest

from protostar.deployer.network_config import (
    NetworkConfig,
    UnknownStarkwareNetworkException,
)


def test_loading_starkware_networks():
    assert (
        NetworkConfig.from_starknet_network_name("alpha-goerli").gateway_url is not None
    )
    assert (
        NetworkConfig.from_starknet_network_name("alpha-mainnet").gateway_url
        is not None
    )


def test_unknown_network_name_error():
    with pytest.raises(UnknownStarkwareNetworkException):
        NetworkConfig.from_starknet_network_name("foobar")


def test_testnet_block_explorer():
    assert (
        NetworkConfig.from_starknet_network_name(
            "alpha-goerli"
        ).get_contract_explorer_url(999)
        == "https://goerli.voyager.online/contract/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )
