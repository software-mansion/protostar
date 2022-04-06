# pylint: disable=redefined-outer-name
from os import chdir, getcwd, path
from pathlib import Path
from subprocess import STDOUT, check_output
from typing import List

import pexpect
import pytest
from pytest_mock import MockerFixture

ACTUAL_CWD = getcwd()


@pytest.fixture(name="home_path")
def home_path_fixture(tmpdir: str) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="protostar_bin_dir_path")
def protostar_bin_dir_path_fixture(home_path) -> Path:
    return home_path / ".protostar" / "dist" / "protostar"


@pytest.fixture(autouse=True)
def protostar_in_path_fixture(mocker: MockerFixture, protostar_bin_dir_path: Path):
    protostar_bin_dir_path.mkdir(parents=True)
    mocker.patch("shutil.which").return_value = protostar_bin_dir_path / "protostar"


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
    child.expect("libraries directory *", timeout=1)
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
