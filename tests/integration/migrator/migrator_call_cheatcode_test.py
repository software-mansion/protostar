import json
from os import listdir
from pathlib import Path
from typing import Dict

import pytest

from protostar.protostar_exception import ProtostarException
from protostar.starknet import ReportedException
from protostar.starknet_gateway.starknet_request import StarknetRequest
from tests.data.contracts import IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.migrator.conftest import MigrateFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True, scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./src/main.cairo": IDENTITY_CONTRACT})
        protostar.build_sync()
        yield protostar


async def test_using_dict_to_pass_args(migrate: MigrateFixture):
    await migrate(
        """
        contract_address = deploy_contract("./build/main.json").contract_address

        result = call(contract_address, "identity", {"arg": 42})

        assert result.res == 42
        """
    )


async def test_failure_on_wrong_args(migrate: MigrateFixture):
    with pytest.raises(ReportedException, match="Input arg not provided"):
        await migrate(
            """
            contract_address = deploy_contract("./build/main.json").contract_address

            call(contract_address, "identity", [])
            """
        )


async def test_failure_when_calling_not_existing_function(migrate: MigrateFixture):
    with pytest.raises(
        ProtostarException, match="unknown function: 'UNKNOWN_FUNCTION'"
    ):
        await migrate(
            """
            contract_address = deploy_contract("./build/main.json").contract_address

            call(contract_address, "UNKNOWN_FUNCTION")
            """
        )


async def test_failure_when_calling_not_existing_contract(migrate: MigrateFixture):
    with pytest.raises(ProtostarException, match="unknown contract"):
        await migrate('call(123, "_")')


async def test_migration_using_call_creates_output(
    protostar: ProtostarFixture, devnet_gateway_url: str
):
    migration_file_path = protostar.create_migration_file(
        """
        contract_address = deploy_contract("./build/main.json").contract_address
        call(contract_address, "identity", [42])
        """
    )
    migration_output_relative_path = Path("./migrations/output")

    migration_history = await protostar.migrate(
        migration_file_path,
        gateway_url=devnet_gateway_url,
        output_dir=migration_output_relative_path,
    )

    loaded_migration_output = load_migration_history_from_output(
        migration_output_path=protostar.project_root_path
        / migration_output_relative_path
    )
    assert loaded_migration_output is not None
    output_file_content = str(loaded_migration_output)
    assert "CALL" in output_file_content
    assert "[42]" in output_file_content
    assert "{'res': 42}" in output_file_content
    contract_address = extract_contract_address_from_deploy_response(
        migration_history.starknet_requests[0].response
    )
    assert str(contract_address) in output_file_content


def load_migration_history_from_output(migration_output_path: Path) -> Dict:
    migration_output_file_names = listdir(migration_output_path)
    assert len(migration_output_file_names) == 1
    migration_output_file_path = migration_output_path / migration_output_file_names[0]
    return load_json(migration_output_file_path)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return json.loads(file.read())


def extract_contract_address_from_deploy_response(
    deploy_response: StarknetRequest.Payload,
) -> int:
    assert isinstance(deploy_response["contract_address"], int)
    return deploy_response["contract_address"]
