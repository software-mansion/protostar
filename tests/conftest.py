# pylint: disable=redefined-outer-name
from os import chdir, getcwd, path
from pathlib import Path
from subprocess import STDOUT, check_output
from typing import List

import pexpect
import pytest

ACTUAL_CWD = Path(getcwd())


@pytest.fixture(autouse=True)
def change_cwd(tmpdir):
    return chdir(tmpdir)


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
    chdir(project_name)
