# pylint: disable=redefined-outer-name
from os import chdir, listdir, path
from pathlib import Path

import pytest
import pexpect

from tests.conftest import ACTUAL_CWD, init_project


def test_help(protostar):
    result = protostar(["--help"])
    assert "usage:" in result


def test_init(project_name: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"./{project_name}")

    init_project(project_name)

    dirs = listdir(project_name)
    assert "protostar.toml" in dirs
    assert ".git" in dirs


def test_init_existing(project_name: str):
    child = pexpect.spawn(
        f"python {path.join(ACTUAL_CWD, 'protostar.py')} init --existing"
    )
    child.expect("Project name:", timeout=5)
    child.sendline("")
    child.expect("Please provide a non-empty project name:", timeout=5)
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
    child.sendline("lib_test")
    child.expect(pexpect.EOF)

    dirs = listdir(".")
    assert "protostar.toml" in dirs
    assert "lib_test" in dirs


def test_init_ask_existing(project_name: str):
    open(Path() / "example.cairo", "a").close()

    child = pexpect.spawn(f"python {path.join(ACTUAL_CWD, 'protostar.py')} init")
    child.expect("There are cairo.*", timeout=10)
    child.sendline("y")
    child.expect("Project name:", timeout=5)
    child.sendline("")
    child.expect("Please provide a non-empty project name:", timeout=5)
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
    child.sendline("lib_test")
    child.expect(pexpect.EOF)

    dirs = listdir(".")
    assert "protostar.toml" in dirs
    assert "lib_test" in dirs
