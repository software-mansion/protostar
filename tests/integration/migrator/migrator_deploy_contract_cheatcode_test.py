from typing import cast

import pytest

from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.migrator.conftest import (
    MigrateFixture,
    assert_transaction_accepted,
)
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True)
def setup(protostar: ProtostarFixture):
    protostar.init_sync()
    protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
    protostar.build_sync()


async def test_deploy_contract(
    protostar: ProtostarFixture, migrate: MigrateFixture, devnet_gateway_url: str
):
    result = await migrate('deploy_contract("./build/main.json", [42])')

    assert len(result.starknet_requests) == 1
    assert result.starknet_requests[0].action == "DEPLOY"
    assert result.starknet_requests[0].payload["contract"] == str(
        (protostar.project_root_path / "build" / "main.json").resolve()
    )
    assert result.starknet_requests[0].payload["constructor_args"] == [42]
    assert result.starknet_requests[0].response["code"] == "TRANSACTION_RECEIVED"

    transaction_hash = cast(
        int, result.starknet_requests[0].response["transaction_hash"]
    )
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)
