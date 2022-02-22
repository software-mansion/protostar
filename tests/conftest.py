# pylint: disable=redefined-outer-name
from os import chdir, getcwd, path
from subprocess import check_output
from typing import List

import pexpect
import pytest

ACTUAL_CWD = getcwd()


@pytest.fixture(autouse=True)
def change_cwd(tmpdir):
    return chdir(tmpdir)


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


def protostar(args: List[str]) -> str:
    return check_output(
        ["python", path.join(ACTUAL_CWD, "protostar.py")] + args
    ).decode("utf-8")


@pytest.fixture
def init(project_name: str):
    init_project(project_name)
