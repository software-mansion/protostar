from datetime import datetime
from os import listdir
from pathlib import Path
from typing import cast

import pytest
from freezegun import freeze_time

from protostar.migrator.migrator_datetime_state import MigratorDateTimeState
from protostar.protostar_exception import ProtostarException
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


@freeze_time("2022-04-02 21:37:42")
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


@freeze_time("2022-04-02 21:37:42")
async def test_deploying_by_contract_name(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file('deploy_contract("main", [42])')

    result = await protostar.migrate(file_path, devnet_gateway_url)

    transaction_hash = extract_transaction_hash(result.starknet_requests[0])
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


@freeze_time("2022-04-02 21:37:43")
async def test_compilation_output_when_deployed_by_name(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file('deploy_contract("main", [42])')

    await protostar.migrate(file_path, devnet_gateway_url)

    compilation_output = create_migration_compilation_output_path(file_path)
    assert not is_directory_empty(compilation_output)


@freeze_time("2022-04-02 21:37:44")
async def test_compilation_output_not_created_when_deploying_by_path(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file(
        'deploy_contract("./build/main.json", [42])'
    )

    await protostar.migrate(file_path, devnet_gateway_url)

    compilation_output = create_migration_compilation_output_path(file_path)
    assert not compilation_output.exists()


@freeze_time("2022-04-02 21:37:45")
async def test_compilation_output_dir_overwrite_protection(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file('deploy_contract("main", [42])')

    await protostar.migrate(file_path, devnet_gateway_url)

    with pytest.raises(ProtostarException):
        await protostar.migrate(file_path, devnet_gateway_url)


async def test_data_transformation(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file(
        'deploy_contract("./build/main.json", {"initial_balance": 42})'
    )

    result = await protostar.migrate(file_path, devnet_gateway_url)

    assert result.starknet_requests[0] is not None


def extract_transaction_hash(starknet_request: StarknetRequest):
    return cast(int, starknet_request.response["transaction_hash"])


def create_migration_compilation_output_path(migration_file: Path) -> Path:
    datetime_prefix = MigratorDateTimeState.get_datetime_prefix(datetime.now())
    return migration_file.parent / f"{datetime_prefix}_{migration_file.stem}"


def is_directory_empty(directory: Path) -> bool:
    dir_content = listdir(directory)
    return len(dir_content) == 0
