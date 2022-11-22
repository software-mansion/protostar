from datetime import datetime
from os import listdir
from pathlib import Path
from typing import cast

import pytest
from freezegun import freeze_time

from protostar.migrator.migrator_datetime_state import MigratorDateTimeState
from protostar.starknet_gateway.starknet_request import StarknetRequest
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.migrator.conftest import (
    MigrateFixture,
    assert_transaction_accepted,
)
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True, name="protostar", scope="module")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
        protostar.build_sync()
        yield protostar


@freeze_time("2022-04-02 21:37:42")
async def test_deploy_contract(migrate: MigrateFixture, devnet_gateway_url: str):
    result = await migrate(
        """
        declaration = declare("./build/main.json")
        deploy_contract(declaration.class_hash, [42])
        """
    )

    assert len(result.starknet_requests) == 2
    assert result.starknet_requests[1].action == "INVOKE_UDC"
    assert isinstance(result.starknet_requests[1].payload["class_hash"], int)
    assert result.starknet_requests[1].payload["constructor_args"] == [42]
    assert result.starknet_requests[1].response["code"] == "TRANSACTION_RECEIVED"

    transaction_hash = extract_transaction_hash(result.starknet_requests[0])
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


@freeze_time("2022-04-02 21:37:42")
async def test_deploying_by_contract_name(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file(
        """
        declaration = declare("main")
        deploy_contract(declaration.class_hash, [42])
        """
    )

    result = await protostar.migrate(file_path, devnet_gateway_url)

    transaction_hash = extract_transaction_hash(result.starknet_requests[0])
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


async def test_data_transformation(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    file_path = protostar.create_migration_file(
        """
        declaration = declare("./build/main.json")
        deploy_contract(declaration.class_hash, {"initial_balance": 42}, abi_path="./build/main_abi.json")
        """
    )

    result = await protostar.migrate(file_path, devnet_gateway_url)

    assert result.starknet_requests[1].payload["constructor_args"] == [42]


def extract_transaction_hash(starknet_request: StarknetRequest):
    return cast(int, starknet_request.response["transaction_hash"])


def create_migration_compilation_output_path(migration_file: Path) -> Path:
    datetime_prefix = MigratorDateTimeState.get_datetime_prefix(datetime.now())
    return migration_file.parent / f"{datetime_prefix}_{migration_file.stem}"


def is_directory_empty(directory: Path) -> bool:
    dir_content = listdir(directory)
    return len(dir_content) == 0
