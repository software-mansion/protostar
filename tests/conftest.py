# pylint: disable=redefined-outer-name
import shutil
from os import chdir, getcwd, mkdir, path
from pathlib import Path
from subprocess import STDOUT, check_output
from typing import List

import pexpect
import pytest

ACTUAL_CWD = Path(getcwd())


@pytest.fixture(autouse=True)
def change_cwd(tmpdir):
    protostar_project_dir = Path(tmpdir) / "protostar_project"
    mkdir(protostar_project_dir)
    yield chdir(protostar_project_dir)
    chdir(ACTUAL_CWD)


@pytest.fixture
def cairo_fixtures_dir():
    return Path(ACTUAL_CWD, "tests", "e2e", "fixtures")


@pytest.fixture
def copy_fixture(cairo_fixtures_dir):
    return lambda file, dst: shutil.copy(cairo_fixtures_dir / file, dst)


@pytest.fixture
def project_name() -> str:
    return "foobar"


@pytest.fixture
def libs_path() -> str:
    return ""


def init_project(project_name: str, libs_path: str):
    child = pexpect.spawn(
        f"{path.join(ACTUAL_CWD, 'dist', 'protostar', 'protostar')} init"
    )
    child.expect(
        "project directory name:", timeout=30
    )  # the very first run is a bit slow
    child.sendline(project_name)
    child.expect("libraries directory *", timeout=1)
    child.sendline(libs_path)
    child.expect(pexpect.EOF)


@pytest.fixture
def protostar():
    def _protostar(args: List[str]) -> str:
        return (
            check_output(
                [path.join(ACTUAL_CWD, "dist", "protostar", "protostar")] + args,
                stderr=STDOUT,
            )
            .decode("utf-8")
            .strip()
        )

    return _protostar

@pytest.fixture
def init(project_name: str, libs_path: str):
    init_project(project_name, libs_path)
    yield chdir(project_name)
    chdir(ACTUAL_CWD)
