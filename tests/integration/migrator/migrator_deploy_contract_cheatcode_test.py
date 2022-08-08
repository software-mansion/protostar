from pathlib import Path
from typing import cast

from protostar.migrator import Migrator
from tests.integration.migrator.conftest import assert_transaction_accepted


async def test_deploy_contract(
    migrator_builder: Migrator.Builder, devnet_gateway_url: str, project_root_path: Path
):

    migrator = await migrator_builder.build(
        project_root_path / "migrations" / "migration_deploy_contract.cairo",
    )

    result = await migrator.run()

    assert len(result.starknet_requests) == 1
    assert result.starknet_requests[0].action == "DEPLOY"
    assert result.starknet_requests[0].payload["contract"] == str(
        (project_root_path / "build" / "main_with_constructor.json").resolve()
    )
    assert result.starknet_requests[0].payload["constructor_args"] == [42]
    assert result.starknet_requests[0].response["code"] == "TRANSACTION_RECEIVED"

    transaction_hash = cast(
        int, result.starknet_requests[0].response["transaction_hash"]
    )
    await assert_transaction_accepted(devnet_gateway_url, transaction_hash)
