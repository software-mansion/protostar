from pathlib import Path

import pytest

from tests.data.contracts import IDENTITY_CONTRACT
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True)
def setup(protostar: ProtostarFixture):
    protostar.init_sync()
    protostar.create_files({"./src/main.cairo": IDENTITY_CONTRACT})
    protostar.build_sync()


@pytest.fixture(name="migration_file_path")
def migration_file_path_fixture(protostar: ProtostarFixture) -> Path:
    return protostar.create_migration_file(
        up_hint_content='deploy_contract("./build/main.json")',
        down_hint_content='declare("./build/main.json")',
    )


async def test_migrate_up(
    protostar: ProtostarFixture, migration_file_path: Path, devnet_gateway_url: str
):
    result = await protostar.migrate(migration_file_path, network=devnet_gateway_url)

    assert result.starknet_requests[0].action == "DEPLOY"


async def test_migrate_down(
    protostar: ProtostarFixture, migration_file_path: Path, devnet_gateway_url: str
):
    result = await protostar.migrate(
        migration_file_path, network=devnet_gateway_url, rollback=True
    )

    assert result.starknet_requests[0].action == "DECLARE"
