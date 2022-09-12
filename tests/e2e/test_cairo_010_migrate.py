from distutils.file_util import copy_file
from pathlib import Path
from subprocess import CalledProcessError

import pytest


@pytest.mark.usefixtures("init")
def test_migrating_file_to_010(
        protostar, datadir: Path
):
    copy_file(
        src=str(datadir / "pre_010_file.cairo"),
        dst="./src/main.cairo",
    )

    protostar(
        ["cairo-migrate", "src"]
    )

    assert (Path(".") / "src" / "main.cairo").read_text() == (datadir / "post_010_file.cairo").read_text()


@pytest.mark.usefixtures("init")
def test_failing_migrate_to_010(
        protostar, datadir: Path
):
    copy_file(
        src=str(datadir / "pre_010_file_unsupported_migrator_syntax.cairo"),
        dst="./src/main.cairo",
    )

    with pytest.raises(CalledProcessError) as exc:
        protostar(
            ["cairo-migrate", "src"]
        )

    assert "Migrate exception" in str(exc.value.output)
    assert "Comments inside expressions are not supported" in str(exc.value.output)
