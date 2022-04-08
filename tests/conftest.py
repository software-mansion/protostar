# pylint: disable=redefined-outer-name
import shutil
from os import chdir, getcwd, mkdir, path
from pathlib import Path
from subprocess import STDOUT, check_output
from typing import List

import pexpect
import pytest

ACTUAL_CWD = getcwd()


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
def project_name():
    return "foobar"


def init_project(project_name: str):
    child = pexpect.spawn(f"python {path.join(ACTUAL_CWD, 'protostar.py')} init")
    child.expect("Project name:", timeout=5)
    child.sendline(project_name)
    child.expect("Project description:", timeout=1)
    child.sendline("")
    child.expect("Author:", timeout=1)
    child.sendline("")
    child.expect("Version:", timeout=1)
    child.sendline("")
    child.expect("License:", timeout=1)
    child.sendline("")
    child.expect("Libraries directory *", timeout=1)
    child.sendline("")
    child.expect(pexpect.EOF)


@pytest.fixture
def protostar():
    def _protostar(args: List[str]) -> str:
        return (
            check_output(
                ["python", path.join(ACTUAL_CWD, "protostar.py")] + args, stderr=STDOUT
            )
            .decode("utf-8")
            .strip()
        )

    return _protostar


@pytest.fixture
def init(project_name: str):
    init_project(project_name)
    yield chdir(project_name)
    chdir(ACTUAL_CWD)
