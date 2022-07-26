from pathlib import Path

from protostar.migrator.migrator import Migrator


async def test_migrate_up(
    migrator_factory: Migrator.Factory, devnet_gateway_url: str, project_root_path: Path
):
    migrator = await migrator_factory.build(
        project_root_path / "migrations" / "migration_down.cairo",
        config=Migrator.Config(gateway_url=devnet_gateway_url),
    )

    result = await migrator.run()
    assert result.starknet_requests[0].action == "DEPLOY"


async def test_migrate_down(
    migrator_factory: Migrator.Factory, devnet_gateway_url: str, project_root_path: Path
):
    migrator = await migrator_factory.build(
        project_root_path / "migrations" / "migration_down.cairo",
        config=Migrator.Config(gateway_url=devnet_gateway_url),
    )

    result = await migrator.run(rollback=True)
    assert result.starknet_requests[0].action == "DECLARE"
