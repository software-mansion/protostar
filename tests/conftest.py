# pylint: disable=redefined-outer-name
from os import chdir, getcwd, path
from subprocess import STDOUT, check_output
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
    child.expect("project directory name:", timeout=5)
    child.sendline(project_name)
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
    chdir(project_name)
