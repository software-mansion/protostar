# pylint: disable=redefined-outer-name
from os import listdir, path
from pathlib import Path

import pexpect
import pytest
import tomli

from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager
from tests.e2e.conftest import ACTUAL_CWD, init_project


def test_help(protostar):
    result = protostar(["--help"])
    assert "usage:" in result


def test_versions(protostar):
    result = protostar(["-v"])
    assert "Protostar" in result
    assert "Cairo-lang" in result


def test_init(project_name: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"./{project_name}")

    init_project(project_name, "")

    dirs = listdir(project_name)

    assert "protostar.toml" in dirs
    assert ".git" in dirs


def test_init_existing():
    child = pexpect.spawn(
        f"python {path.join(ACTUAL_CWD, 'binary_entrypoint.py')} init --existing"
    )
    child.expect("libraries directory *", timeout=10)
    child.sendline("lib_test")
    child.expect(pexpect.EOF)

    dirs = listdir(".")
    assert "protostar.toml" in dirs
    assert "lib_test" in dirs
    assert ".git" in dirs


def test_init_ask_existing():
    open(Path() / "example.cairo", "a").close()

    child = pexpect.spawn(
        f"python {path.join(ACTUAL_CWD, 'binary_entrypoint.py')} init"
    )
    child.expect("Your current directory.*", timeout=10)
    child.sendline("y")
    child.expect("libraries directory *", timeout=1)
    child.sendline("lib_test")
    child.expect(pexpect.EOF)

    dirs = listdir(".")
    assert "protostar.toml" in dirs
    assert "lib_test" in dirs
    assert ".git" in dirs


@pytest.mark.usefixtures("init")
def test_protostar_version_in_config_file():
    version_manager = VersionManager(
        ProtostarDirectory(ACTUAL_CWD / "dist" / "protostar")
    )
    assert version_manager.protostar_version is not None

    with open("./protostar.toml", "r+", encoding="UTF-8") as protostar_toml:
        raw_protostar_toml = protostar_toml.read()
        protostar_toml_dict = tomli.loads(raw_protostar_toml)
        version_str = protostar_toml_dict["protostar.config"]["protostar_version"]
        protostar_version = VersionManager.parse(version_str)

        assert version_manager.protostar_version == protostar_version
