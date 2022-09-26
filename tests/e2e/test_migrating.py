import json
import re
from os import listdir
from pathlib import Path
from shutil import copyfile

import pytest
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from tests.conftest import Credentials
from tests.e2e.conftest import ProtostarFixture


def count_hex64(x: str) -> int:
    return len(re.findall(r"0x[0-9a-f]{64}", x))


@pytest.mark.usefixtures("init")
def test_migrating_base_case(
    protostar: ProtostarFixture, devnet_gateway_url, datadir: Path
):
    protostar(["build"])
    migrations_dir_path = Path("./migrations")
    migrations_dir_path.mkdir()
    copyfile(
        src=str(datadir / "migration_up_down.cairo"),
        dst=str(migrations_dir_path / "migration.cairo"),
    )

    result = protostar(
        [
            "--no-color",
            "migrate",
            "migrations/migration.cairo",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--no-confirm",
            "--output-dir",
            "migrations/output",
        ]
    )

    assert "Migration completed" in result
    assert len(listdir((migrations_dir_path / "output"))) == 1
    assert count_hex64(result) == 2


@pytest.mark.usefixtures("init")
async def test_migrating_with_signed_invoke(
    protostar: ProtostarFixture,
    devnet_gateway_url,
    datadir: Path,
    signing_credentials: Credentials,
    monkeypatch,
):
    migrations_dir_path = Path("./migrations")
    src_dir_path = Path("./src")
    migrations_dir_path.mkdir()
    copyfile(
        src=str(datadir / "migration_signed_invokes.cairo"),
        dst=str(migrations_dir_path / "migration.cairo"),
    )

    copyfile(
        src=str(datadir / "box_contract.cairo"),
        dst=str(src_dir_path / "main.cairo"),
    )

    protostar(["build"])

    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, signing_credentials.private_key)
    result = protostar(
        [
            "--no-color",
            "migrate",
            "migrations/migration.cairo",
            "--gateway-url",
            devnet_gateway_url,
            "--account-address",
            signing_credentials.account_address,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--no-confirm",
            "--output-dir",
            "migrations/output",
        ]
    )

    assert "Migration completed" in result

    migration_file = next(migrations_dir_path.glob("output/*.json"))
    with migration_file.open("r", encoding="utf-8") as file:
        migration_content = json.load(file)

    gateway_client = GatewayClient(devnet_gateway_url)

    transactions = [
        await gateway_client.get_transaction(action["response"]["hash"])
        for action in migration_content["starknet_requests"]
        if action["action"] == "INVOKE"
    ]

    assert len(transactions) == 2

    for tx in transactions:
        assert isinstance(tx.signature, list)
        assert len(tx.signature) == 2


@pytest.mark.usefixtures("init")
def test_migrating_with_invoke_and_no_account_address(
    protostar: ProtostarFixture,
    devnet_gateway_url,
    datadir: Path,
):
    migrations_dir_path = Path("./migrations")
    migrations_dir_path.mkdir()
    copyfile(
        src=str(datadir / "migration_signed_invokes.cairo"),
        dst=str(migrations_dir_path / "migration.cairo"),
    )

    protostar(["build"])

    output = protostar(
        [
            "--no-color",
            "migrate",
            "migrations/migration.cairo",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--no-confirm",
            "--output-dir",
            "migrations/output",
        ],
        expect_exit_code=1,
    )
    assert "Account address is required" in output
