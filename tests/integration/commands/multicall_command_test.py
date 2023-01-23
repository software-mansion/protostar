import json
from pathlib import Path
from textwrap import dedent

import pytest
from starknet_py.net.models import StarknetChainId
from pytest import CaptureFixture

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway.multicall import (
    prepare_multicall_file_example,
    Identifier,
)
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture
from tests.conftest import DevnetFixture, SetPrivateKeyEnvVarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="standard_contract_class_hash")
async def standard_contract_class_hash_fixture(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    capsys: CaptureFixture[str],
):
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
        return declare_result.class_hash


@pytest.fixture(name="multicall_file_path")
async def multicall_file_path_fixture(
    standard_contract_class_hash: int,
    tmp_path: Path,
) -> Path:

    multicall_doc_path = tmp_path / "multicall.toml"
    file_content = prepare_multicall_file_example(
        class_hash=standard_contract_class_hash
    )
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


async def test_atomicity(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    standard_contract_class_hash: int,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    tmp_path: Path,
):
    account = devnet.get_predeployed_accounts()[0]
    with set_private_key_env_var(account.private_key):
        deploy_result = await protostar.deploy(
            class_hash=standard_contract_class_hash,
            account_address=account.address,
            max_fee="auto",
            gateway_url=devnet.get_gateway_url(),
        )
        multicall_file_path = tmp_path / "calls.toml"
        multicall_file_path.write_text(
            dedent(
                f"""
            [[call]]
            type = "invoke"
            function = "increase_balance"
            contract-address = {deploy_result.address}
            inputs = [42]

            [[call]]
            type = "invoke"
            function = "increase_balance"
            contract-address = {deploy_result.address}
            inputs = [3618502788666131213697322783095070105623107215331596699973092056135872020480]
        """
            )
        )

        with pytest.raises(ProtostarException):
            await protostar.multicall(
                file_path=multicall_file_path,
                account=devnet.get_predeployed_accounts()[0],
                gateway_url=devnet.get_gateway_url(),
            )

        result = await protostar.call(
            contract_address=deploy_result.address,
            function_name="get_balance",
            gateway_url=devnet.get_gateway_url(),
            inputs=[],
        )
        assert result.call_output.cairo_data == [0]
