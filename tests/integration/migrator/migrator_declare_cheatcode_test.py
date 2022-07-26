import re
from pathlib import Path

import pytest

from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator


async def test_declare_contract(
    migrator_factory: Migrator.Factory, devnet_gateway_url: str, project_root_path: Path
):

    migrator = await migrator_factory.build(
        project_root_path / "migrations" / "migration_declare.cairo",
        config=Migrator.Config(gateway_url=devnet_gateway_url),
    )

    result = await migrator.run("up")

    assert len(result.starknet_requests) == 1
    assert result.starknet_requests[0].action == "DECLARE"
    assert result.starknet_requests[0].payload["contract"] == str(
        (project_root_path / "build" / "main_with_constructor.json").resolve()
    )
    assert result.starknet_requests[0].response["code"] == "TRANSACTION_RECEIVED"


async def test_descriptive_error_on_file_not_found(
    migrator_factory: Migrator.Factory, devnet_gateway_url: str, project_root_path: Path
):
    migrator = await migrator_factory.build(
        project_root_path / "migrations" / "migration_declare_file_not_found.cairo",
        config=Migrator.Config(gateway_url=devnet_gateway_url),
    )

    with pytest.raises(
        CheatcodeException,
        match=re.compile(
            "Couldn't find `.*/NOT_EXISTING_FILE.json`",
        ),
    ):
        await migrator.run("up")
