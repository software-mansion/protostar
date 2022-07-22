from pathlib import Path

import pytest

from protostar.migrator import Migrator
from protostar.migrator.migrator_execution_environment import \
    MigratorExecutionEnvironment
from protostar.starknet_gateway.gateway_facade import GatewayFacade


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(shared_datadir: Path) -> Path:
    return shared_datadir


@pytest.fixture(name="migrator_factory")
def migrator_factory_fixture(project_root_path: Path):
    return Migrator.Factory(
        migrator_execution_environment_factory=MigratorExecutionEnvironment.Factory(
            gateway_facade=GatewayFacade(project_root_path)
        )
    )
