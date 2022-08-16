import re
from pathlib import Path
from typing import cast

import pytest

from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator
from protostar.starknet_gateway import GatewayFacade
from tests.integration.migrator.conftest import assert_transaction_accepted


async def test_declare_contract(
    migrator_builder: Migrator.Builder,
    devnet_gateway_url: str,
    project_root_path: Path,
    gateway_facade: GatewayFacade,
):
    migrator = await migrator_builder.build(
        project_root_path / "migrations" / "migration_declare.cairo",
        gateway_facade=gateway_facade,
    )

    result = await migrator.run()

    assert len(result.starknet_requests) == 1
    assert result.starknet_requests[0].action == "DECLARE"
    assert result.starknet_requests[0].payload["contract"] == str(
        (project_root_path / "build" / "main_with_constructor.json").resolve()
    )
    assert result.starknet_requests[0].response["code"] == "TRANSACTION_RECEIVED"
    transaction_hash = cast(
        int, result.starknet_requests[0].response["transaction_hash"]
    )
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)


async def test_descriptive_error_on_file_not_found(
    migrator_builder: Migrator.Builder,
    project_root_path: Path,
    gateway_facade: GatewayFacade,
):
    migrator = await migrator_builder.build(
        project_root_path / "migrations" / "migration_declare_file_not_found.cairo",
        gateway_facade=gateway_facade,
    )

    with pytest.raises(
        CheatcodeException,
        match=re.compile(
            "Couldn't find `.*/NOT_EXISTING_FILE.json`",
        ),
    ):
        await migrator.run()
