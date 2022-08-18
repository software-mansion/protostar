from typing import cast

import pytest

from protostar.starknet_gateway.starknet_request import StarknetRequest
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

    transaction_hash = extract_transaction_hash(result.starknet_requests[0])
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


async def test_deploying_by_contract_name(
    migrate: MigrateFixture, devnet_gateway_url: str
):
    result = await migrate('deploy_contract("main", [42])')

    transaction_hash = extract_transaction_hash(result.starknet_requests[0])
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


def extract_transaction_hash(starknet_request: StarknetRequest):
    return cast(int, starknet_request.response["transaction_hash"])
