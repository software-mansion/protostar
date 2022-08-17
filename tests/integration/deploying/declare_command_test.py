from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
from pytest_mock import MockerFixture
from starknet_py.net.models import StarknetChainId

from protostar.cli.signable_command_mixin import PRIVATE_KEY_ENV_VAR_NAME
from protostar.commands.declare.declare_command import DeclareCommand


@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_declaring_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
    monkeypatch,
):
    declare_command = DeclareCommand(
        logger=mocker.MagicMock(),
        project_root_path=project_root_path,
    )
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "123")
    args = SimpleNamespace()
    args.chain_id = StarknetChainId.TESTNET.value
    args.signer_class = None
    args.account_address = "123"
    args.private_key_path = None
    args.contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.network = None
    args.token = None
    args.wait_for_acceptance = False

    response = await declare_command.run(args)

    assert response.class_hash is not None


@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract_with_signing(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
    monkeypatch,
):
    declare_command = DeclareCommand(
        logger=mocker.MagicMock(),
        project_root_path=project_root_path,
    )
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "123")
    args = SimpleNamespace()
    args.chain_id = StarknetChainId.TESTNET.value
    args.signer_class = None
    args.account_address = "123"
    args.private_key_path = None
    args.contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.network = None
    args.token = None
    args.wait_for_acceptance = True

    response = await declare_command.run(args)

    assert response.class_hash is not None

    # TODO: Use GatewayClient when devnet fixes: https://github.com/Shard-Labs/starknet-devnet/issues/225
    resp = requests.get(
        f"{devnet_gateway_url}/feeder_gateway/get_transaction?transactionHash={str(hex(response.transaction_hash))}"
    ).json()

    assert "transaction" in resp
    assert "signature" in resp["transaction"]
    assert resp["transaction"]["signature"] == [
        "3459263272550625393812584460277149848351409720716906360199187355059506361232",
        "1830633873577487268914590325347030490499699872026627682646826922183589844384",
    ]


def test_account_doesnt_exist():
    pass  # TODO: Implement in 0.10
