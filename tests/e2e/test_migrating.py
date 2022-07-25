from pathlib import Path
from shutil import copyfile

import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.usefixtures("init")
def test_migrating_base_case(
    protostar: ProtostarFixture, devnet_gateway_url, datadir: Path
):
    protostar(["build"])
    migrations_dir_path = Path("./migrations")
    migrations_dir_path.mkdir()
    copyfile(
        src=str(datadir / "migration_up_down.cairo"),
        dst=str(migrations_dir_path / "migration.cairo"),
    )

    result = protostar(
        [
            "--no-color",
            "migrate",
            "migrations/migration.cairo",
            "--gateway-url",
            devnet_gateway_url,
            "--no-confirm",
        ]
    )

    assert "Migration completed" in result
