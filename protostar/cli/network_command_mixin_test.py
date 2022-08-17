from types import SimpleNamespace

import pytest
from protostar.cli.network_command_mixin import (
    NetworkCommandMixin,
    GATEWAY_URL_ARG_NAME,
    NETWORK_ARG_NAME,
)
from protostar.protostar_exception import ProtostarException


@pytest.mark.parametrize(
    "network, result_gateway_url",
    (
        ("testnet", "https://alpha4.starknet.io/gateway"),
        ("mainnet", "https://alpha-mainnet.starknet.io/gateway"),
        ("alpha-goerli", "https://alpha4.starknet.io/gateway"),
        ("alpha-mainnet", "https://alpha-mainnet.starknet.io/gateway"),
    ),
)
def test_network_config_from_literal(mocker, network, result_gateway_url):
    args = SimpleNamespace()
    args.network = network
    args.gateway_url = None
    args.chain_id = None
    logger = mocker.MagicMock()

    config = NetworkCommandMixin.get_network_config(args, logger)
    assert config.gateway_url == result_gateway_url


def test_mixin_throws_on_incorrect_network_name(mocker):
    args = SimpleNamespace()
    args.network = "abcdef"
    args.gateway_url = None
    args.chain_id = None
    logger = mocker.MagicMock()
    with pytest.raises(ProtostarException) as pex:
        NetworkCommandMixin.get_network_config(args, logger)

    assert "Unknown StarkNet network" in pex.value.message


def test_mixin_throws_on_no_chain_id_with_custom_gateway_url(mocker):
    args = SimpleNamespace()
    args.network = None
    args.gateway_url = "https://randomurl.com"
    args.chain_id = None
    logger = mocker.MagicMock()
    with pytest.raises(ProtostarException) as pex:
        NetworkCommandMixin.get_network_config(args, logger)

    assert "Argument `chain-id` is required" in pex.value.message


def test_mixin_throws_on_no_sufficient_args(mocker):
    args = SimpleNamespace()
    args.network = None
    args.gateway_url = None
    args.chain_id = None
    logger = mocker.MagicMock()
    with pytest.raises(ProtostarException) as pex:
        NetworkCommandMixin.get_network_config(args, logger)

    assert (
        f"Argument `{GATEWAY_URL_ARG_NAME}` or `{NETWORK_ARG_NAME}` is required"
        in pex.value.message
    )
