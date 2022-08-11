from pathlib import Path
from typing import cast

from protostar.migrator import Migrator
from tests.integration.migrator.conftest import (
    RunMigrateFixture,
    assert_transaction_accepted,
)


async def test_call_contract(run_migrate: RunMigrateFixture):
    migration_history = await run_migrate("migration_declare.cairo")

    assert_migration_history_includes_call_request(migration_history)
    assert_migration_history_includes_call_response(migration_history)
