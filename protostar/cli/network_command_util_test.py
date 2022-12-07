import re
from types import SimpleNamespace
from typing import Optional, Protocol

import pytest

from protostar.cli.network_command_util import (
    GATEWAY_URL_ARG_NAME,
    NETWORK_ARG_NAME,
    NetworkCommandUtil,
)
from protostar.protostar_exception import ProtostarException


class CreateNetworkCommandUtilFixture(Protocol):
    def __call__(
        self, network: Optional[str] = None, chain_id: Optional[int] = None
    ) -> NetworkCommandUtil:
        ...


@pytest.fixture(name="create_network_command_util")
def create_network_command_util_fixture() -> CreateNetworkCommandUtilFixture:
    def create_network_command_util(
        network: Optional[str] = None, chain_id: Optional[int] = None
    ):
        args = SimpleNamespace()
        args.network = network
        args.gateway_url = None
        args.chain_id = chain_id
        return NetworkCommandUtil(args)

    return create_network_command_util


@pytest.mark.parametrize(
    "network, result_gateway_url",
    (
        ("testnet", "https://alpha4.starknet.io"),
        ("mainnet", "https://alpha-mainnet.starknet.io"),
    ),
)
def test_network_config_from_literal(network: str, result_gateway_url: str):
    args = SimpleNamespace()
    args.network = network
    args.gateway_url = None
    args.chain_id = None
    config = NetworkCommandUtil(args).get_network_config()
    assert config.gateway_url == result_gateway_url


def test_mixin_throws_on_incorrect_network_name():
    args = SimpleNamespace()
    args.network = "abcdef"
    args.gateway_url = None
    args.chain_id = None
    with pytest.raises(ProtostarException, match=re.escape("Unknown StarkNet network")):
        NetworkCommandUtil(args).get_network_config()


def test_mixin_throws_on_no_chain_id_with_custom_gateway_url():
    args = SimpleNamespace()
    args.network = None
    args.gateway_url = "https://randomurl.com"
    args.chain_id = None
    with pytest.raises(
        ProtostarException, match=re.escape("Argument `chain-id` is required")
    ):
        NetworkCommandUtil(args).get_network_config()


def test_mixin_throws_on_no_sufficient_args():
    args = SimpleNamespace()
    args.network = None
    args.gateway_url = None
    args.chain_id = None
    with pytest.raises(
        ProtostarException,
        match=re.escape(
            f"Argument `{GATEWAY_URL_ARG_NAME}` or `{NETWORK_ARG_NAME}` is required"
        ),
    ):
        NetworkCommandUtil(args).get_network_config()


def test_printing_invalid_chain_id(
    create_network_command_util: CreateNetworkCommandUtilFixture,
):
    network_command_util = create_network_command_util(chain_id=123)

    with pytest.raises(ProtostarException) as ex:
        network_command_util.get_network_config()

        assert "23448594291968334" in str(ex)
        assert "1536727068981429685321" in str(ex)
