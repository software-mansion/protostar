from pathlib import Path

from protostar.migrator import Migrator


async def test_deploy_contract(
    migrator_factory: Migrator.Factory, devnet_gateway_url: str, project_root_path: Path
):

    migrator = await migrator_factory.build(
        project_root_path / "migrations" / "migration_deploy_contract.cairo",
        config=Migrator.Config(gateway_url=devnet_gateway_url),
    )

    result = await migrator.run("up")

    assert len(result.starknet_interactions) == 2
    assert result.starknet_interactions[0].action == "DEPLOY"
    assert result.starknet_interactions[0].direction == "TO_STARKNET"
    assert result.starknet_interactions[0].payload["contract"] == str(
        (project_root_path / "build" / "main_with_constructor.json").resolve()
    )
    assert result.starknet_interactions[0].payload["constructor_args"] == [42]

    assert result.starknet_interactions[1].action == "DEPLOY"
    assert result.starknet_interactions[1].direction == "FROM_STARKNET"
    assert result.starknet_interactions[1].payload["code"] == "TRANSACTION_RECEIVED"
