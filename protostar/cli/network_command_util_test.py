from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from protostar.cli.network_command_util import (
    NetworkCommandUtil,
    GATEWAY_URL_ARG_NAME,
    NETWORK_ARG_NAME,
)
from protostar.protostar_exception import ProtostarException


@pytest.mark.parametrize(
    "network, result_gateway_url",
    (
        ("testnet", "https://alpha4.starknet.io"),
        ("mainnet", "https://alpha-mainnet.starknet.io"),
        ("alpha-goerli", "https://alpha4.starknet.io"),
        ("alpha-mainnet", "https://alpha-mainnet.starknet.io"),
    ),
)
def test_network_config_from_literal(
    mocker: MockerFixture, network: str, result_gateway_url: str
):
    args = SimpleNamespace()
    args.network = network
    args.gateway_url = None
    args.chain_id = None
    logger = mocker.MagicMock()

    config = NetworkCommandUtil(args, logger).get_network_config()
    assert config.gateway_url == result_gateway_url


def test_mixin_throws_on_incorrect_network_name(mocker: MockerFixture):
    args = SimpleNamespace()
    args.network = "abcdef"
    args.gateway_url = None
    args.chain_id = None
    logger = mocker.MagicMock()
    with pytest.raises(ProtostarException) as pex:
        NetworkCommandUtil(args, logger).get_network_config()

    assert "Unknown StarkNet network" in pex.value.message


def test_mixin_throws_on_no_chain_id_with_custom_gateway_url(mocker: MockerFixture):
    args = SimpleNamespace()
    args.network = None
    args.gateway_url = "https://randomurl.com"
    args.chain_id = None
    logger = mocker.MagicMock()
    with pytest.raises(ProtostarException) as pex:
        NetworkCommandUtil(args, logger).get_network_config()

    assert "Argument `chain-id` is required" in pex.value.message


def test_mixin_throws_on_no_sufficient_args(mocker: MockerFixture):
    args = SimpleNamespace()
    args.network = None
    args.gateway_url = None
    args.chain_id = None
    logger = mocker.MagicMock()
    with pytest.raises(ProtostarException) as pex:
        NetworkCommandUtil(args, logger).get_network_config()

    assert (
        f"Argument `{GATEWAY_URL_ARG_NAME}` or `{NETWORK_ARG_NAME}` is required"
        in pex.value.message
    )
