from pathlib import Path

from protostar.migrator.migrator import Migrator
from protostar.starknet_gateway import GatewayFacade


async def test_migrate_up(
    migrator_builder: Migrator.Builder,
    project_root_path: Path,
    gateway_facade: GatewayFacade,
):
    migrator = await migrator_builder.build(
        project_root_path / "migrations" / "migration_down.cairo", gateway_facade
    )

    result = await migrator.run()
    assert result.starknet_requests[0].action == "DEPLOY"


async def test_migrate_down(
    migrator_builder: Migrator.Builder,
    project_root_path: Path,
    gateway_facade: GatewayFacade,
):
    migrator = await migrator_builder.build(
        project_root_path / "migrations" / "migration_down.cairo", gateway_facade
    )

    result = await migrator.run(rollback=True)
    assert result.starknet_requests[0].action == "DECLARE"
