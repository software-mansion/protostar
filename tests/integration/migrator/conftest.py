from pathlib import Path
from typing import Union

import pytest
from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from protostar.migrator import Migrator
from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway.gateway_facade import GatewayFacade


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(shared_datadir: Path) -> Path:
    return shared_datadir


@pytest.fixture(name="migrator_builder")
def migrator_builder_fixture(project_root_path: Path):
    return Migrator.Builder(
        migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(
            gateway_facade=GatewayFacade(project_root_path)
        )
    )


async def assert_transaction_accepted(
    devnet_gateway_url: str, transaction_hash: Union[str, int]
):
    gateway = GatewayClient(devnet_gateway_url, chain=StarknetChainId.TESTNET)
    (_, transaction_status) = await gateway.wait_for_tx(
        transaction_hash, wait_for_accept=True
    )
    assert transaction_status == TransactionStatus.ACCEPTED_ON_L2
