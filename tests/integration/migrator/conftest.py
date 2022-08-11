from enum import Enum
from pathlib import Path
from typing import Union

import pytest
from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from typing_extensions import Literal, Protocol

from protostar.migrator import Migrator
from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway.gateway_facade import GatewayFacade


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(shared_datadir: Path) -> Path:
    return shared_datadir


@pytest.fixture(name="migrator_builder")
def migrator_builder_fixture(devnet_gateway_url: str, project_root_path: Path):
    migrator_builder = Migrator.Builder(
        migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(),
        gateway_facade_builder=GatewayFacade.Builder(project_root_path),
    )

    migrator_builder.set_network(devnet_gateway_url)

    return migrator_builder


async def assert_transaction_accepted(
    devnet_gateway_url: str, transaction_hash: Union[str, int]
):
    gateway = GatewayClient(devnet_gateway_url, chain=StarknetChainId.TESTNET)
    (_, transaction_status) = await gateway.wait_for_tx(
        transaction_hash, wait_for_accept=True
    )
    assert transaction_status == TransactionStatus.ACCEPTED_ON_L2


MigrationFileName = Literal[
    "migration_declare_file_not_found.cairo",
    "migration_declare.cairo",
    "migration_deploy_contract.cairo",
    "migration_down.cairo",
    "migration_deploy_and_call.cairo",
]


class RunMigrateFixture(Protocol):
    async def __call__(
        self, migration_file_name: MigrationFileName, rollback=False
    ) -> Migrator.History:
        ...


@pytest.fixture(name="run_migrate")
async def run_migrate_fixture(
    migrator_builder: Migrator.Builder, project_root_path: Path
) -> RunMigrateFixture:
    async def run_migrate(
        migration_file_name: MigrationFileName, rollback=False
    ) -> Migrator.History:
        migrator = await migrator_builder.build(
            migration_file_path=project_root_path / "migrations" / migration_file_name,
        )
        return await migrator.run(rollback)

    return run_migrate


class ContractMainWithConstructorDefaults(Enum):
    INITIAL_BALANCE = 0
