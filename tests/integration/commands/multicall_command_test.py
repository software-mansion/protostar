import json
from pathlib import Path

import pytest
from starknet_py.net.models import StarknetChainId
from pytest import CaptureFixture

from protostar.starknet_gateway.multicall import (
    prepare_multicall_file_example,
    Identifier,
)
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture
from tests.conftest import DevnetFixture, SetPrivateKeyEnvVarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="multicall_file_path")
async def multicall_file_path_fixture(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    capsys: CaptureFixture[str],
    tmp_path: Path,
) -> Path:
    account = devnet.get_predeployed_accounts()[0]
    with set_private_key_env_var(account.private_key):
        declare_result = await protostar.declare(
            contract=Path() / "build" / "main.json",
            account_address=account.address,
            chain_id=StarknetChainId.TESTNET,
            wait_for_acceptance=True,
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
        )
    capsys.readouterr()
    multicall_doc_path = tmp_path / "multicall.toml"
    file_content = prepare_multicall_file_example(class_hash=declare_result.class_hash)
    multicall_doc_path.write_text(file_content)
    return multicall_doc_path


async def test_happy_case(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    capsys: CaptureFixture[str],
    multicall_file_path: Path,
):
    result = await protostar.multicall(
        file_path=multicall_file_path,
        account=devnet.get_predeployed_accounts()[0],
        gateway_url=devnet.get_gateway_url(),
    )
    logged_result = capsys.readouterr().out

    await devnet.assert_transaction_accepted(result.transaction_hash)
    assert result.deployed_contract_addresses[Identifier("my_contract")] is not None
    assert f"0x{result.transaction_hash:064x}" in logged_result


async def test_json(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    capsys: CaptureFixture[str],
    multicall_file_path: Path,
):
    result = await protostar.multicall(
        file_path=multicall_file_path,
        account=devnet.get_predeployed_accounts()[0],
        gateway_url=devnet.get_gateway_url(),
        json=True,
    )
    logged_result = capsys.readouterr().out
    parsed_json = json.loads(logged_result)

    await devnet.assert_transaction_accepted(result.transaction_hash)
    assert parsed_json["transaction_hash"] == f"0x{result.transaction_hash:064x}"
    assert parsed_json["my_contract"] == str(
        result.deployed_contract_addresses[Identifier("my_contract")]
    )
