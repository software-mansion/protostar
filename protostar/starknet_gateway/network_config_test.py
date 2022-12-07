from protostar.starknet_gateway.network_config import NetworkConfig


def test_loading_starkware_networks():
    assert NetworkConfig.from_starknet_network_name("testnet").gateway_url is not None
    assert NetworkConfig.from_starknet_network_name("mainnet").gateway_url is not None


def test_testnet_block_explorer():
    assert (
        NetworkConfig.from_starknet_network_name("testnet").get_contract_explorer_url(
            999
        )
        == "https://goerli.voyager.online/contract/0x00000000000000000000000000000000000000000000000000000000000003e7"
    )
