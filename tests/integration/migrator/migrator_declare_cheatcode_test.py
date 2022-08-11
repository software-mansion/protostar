import asyncio
import re
from pathlib import Path
from typing import cast

import pytest

from protostar.protostar_exception import ProtostarException
from tests.integration.migrator.conftest import assert_transaction_accepted
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(scope="module")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True, scope="module")
# pylint: disable=unused-argument
async def setup(protostar: ProtostarFixture):
    await protostar.init()
    protostar.create_files(
        {
            "./src/main.json": """
                %lang starknet

                @view
                func identity(arg) -> (res : felt):
                    return (arg)
                end
            """
        }
    )
    await protostar.build()


async def test_declare_contract(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    protostar_project_root_path: Path,
):
    migration_file_path = protostar.create_migration('declare("./build/main.json")')

    result = await protostar.migrate(migration_file_path, devnet_gateway_url)

    assert len(result.starknet_requests) == 1
    assert result.starknet_requests[0].action == "DECLARE"
    assert result.starknet_requests[0].payload["contract"] == str(
        (protostar_project_root_path / "build" / "main.json").resolve()
    )
    assert result.starknet_requests[0].response["code"] == "TRANSACTION_RECEIVED"
    transaction_hash = cast(
        int, result.starknet_requests[0].response["transaction_hash"]
    )
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


async def test_descriptive_error_on_file_not_found(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
):
    migration_file_path = protostar.create_migration(
        'declare("./NOT_EXISTING_FILE.json")'
    )

    with pytest.raises(
        ProtostarException,
        match=re.compile(
            "Couldn't find `.*/NOT_EXISTING_FILE.json`",
        ),
    ):
        await protostar.migrate(migration_file_path, network=devnet_gateway_url)
