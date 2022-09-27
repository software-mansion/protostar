from pathlib import Path
from typing import Union, Optional

import pytest
from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from typing_extensions import Protocol

from protostar.migrator import Migrator
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(shared_datadir: Path) -> Path:
    return shared_datadir


async def assert_transaction_accepted(
    devnet_gateway_url: str, transaction_hash: Union[str, int]
):
    gateway = GatewayClient(devnet_gateway_url)
    (_, transaction_status) = await gateway.wait_for_tx(
        transaction_hash, wait_for_accept=True
    )
    assert transaction_status == TransactionStatus.ACCEPTED_ON_L2


class MigrateFixture(Protocol):
    async def __call__(
        self, migration_hint_content: str, account_address: Optional[str] = None
    ) -> Migrator.History:
        ...


@pytest.fixture(name="migrate")
async def migrate_fixture(protostar: ProtostarFixture, devnet_gateway_url: str):
    async def migrate(
        migration_hint_content: str, account_address: Optional[str] = None
    ):
        migration_file_path = protostar.create_migration_file(migration_hint_content)
        return await protostar.migrate(
            migration_file_path,
            network=devnet_gateway_url,
            account_address=account_address,
        )

    return migrate
