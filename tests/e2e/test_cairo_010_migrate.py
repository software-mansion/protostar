from distutils.file_util import copy_file
from pathlib import Path

import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.usefixtures("init")
def test_migrating_file_to_010(protostar: ProtostarFixture, datadir: Path):
    copy_file(
        src=str(datadir / "pre_010_file.cairo09"),
        dst="./src/main.cairo",
    )

    protostar(["cairo-migrate", "src"])

    assert (
        Path("src/main.cairo").read_text()
        == (datadir / "post_010_file.cairo").read_text()
    )


@pytest.mark.usefixtures("init")
def test_failing_migrate_to_010(protostar: ProtostarFixture, datadir: Path):
    copy_file(
        src=str(datadir / "pre_010_file_unsupported_migrator_syntax.cairo09"),
        dst="./src/main.cairo",
    )

    output = protostar(["cairo-migrate", "src"], expect_exit_code=1)

    assert "Migrate exception" in output
    assert "Comments inside expressions are not supported" in output
