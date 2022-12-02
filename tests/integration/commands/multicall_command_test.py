from pathlib import Path
from textwrap import dedent

import pytest
from starknet_py.net.models import StarknetChainId
from pytest import CaptureFixture

from protostar.starknet_gateway.multicall.multicall_structs import Identifier
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture
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
) -> int:
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


async def test_multicall_command(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    standard_contract_class_hash: int,
):
    multicall_doc_path = tmp_path / "multicall.toml"
    multicall_doc_path.write_text(
        dedent(
            f"""
        [[call]]
        id = "A"
        type = "deploy"
        class-hash = {standard_contract_class_hash}
        calldata = []

        [[call]]
        type = "invoke"
        contract-address = "$A"
        entrypoint-name = "increase_balance"
        calldata = [42]
    """
        )
    )

    result = await protostar.multicall(
        file_path=multicall_doc_path,
        account=devnet.get_predeployed_accounts()[0],
        gateway_url=devnet.get_gateway_url(),
    )
    logged_result = capsys.readouterr().out

    await devnet.assert_transaction_accepted(result.transaction_hash)
    assert result.deployed_contract_addresses[Identifier("A")] is not None
    assert f"0x{result.transaction_hash:064x}" in logged_result
