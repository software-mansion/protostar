from pathlib import Path

import pytest
import requests
from starknet_py.net.models import StarknetChainId

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_declaring_contract(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    compiled_contract_filepath: Path,
    monkeypatch,
):
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "123")

    response = await protostar.declare(
        chain_id=StarknetChainId.TESTNET.value,
        account_address="123",
        contract=compiled_contract_filepath,
        gateway_url=devnet_gateway_url,
    )

    assert response.class_hash is not None


@pytest.mark.xfail(
    reason="This test is going to fail since sending signed deploy txs is supported only for devnet, and now it's "
    "disabled "
)
@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract_with_signing(
    devnet_gateway_url: str,
    protostar: ProtostarFixture,
    compiled_contract_filepath: Path,
    monkeypatch,
):
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "123")

    response = await protostar.declare(
        chain_id=StarknetChainId.TESTNET.value,
        account_address="123",
        contract=compiled_contract_filepath,
        gateway_url=devnet_gateway_url,
        wait_for_acceptance=True,
    )

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
