# pylint: disable=redefined-outer-name
import re
from os import listdir
from pathlib import Path

import pexpect
import pytest
import tomli
import packaging
from packaging.version import parse as parse_version
from packaging.version import Version


from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


def test_help(protostar):
    result = protostar(["--help"])
    assert "usage:" in result


def test_versions(protostar):
    result = protostar(["-v"])
    assert "Protostar" in result
    assert "Cairo-lang" in result


def test_init(init_project, project_name: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"./{project_name}")

    init_project(override_libs_path="")

    dirs = listdir(project_name)

    assert "protostar.toml" in dirs
    assert ".git" in dirs


def test_init_existing(protostar_bin: Path):
    child = pexpect.spawn(f"{protostar_bin} init --existing")
    child.expect("libraries directory *", timeout=10)
    child.sendline("lib_test")
    child.expect(pexpect.EOF)
    dirs = listdir(".")

    assert "protostar.toml" in dirs
    assert "lib_test" in dirs
    assert ".git" in dirs


def test_init_ask_existing(protostar_bin: Path):
    open(Path() / "example.cairo", "a", encoding="utf-8").close()

    child = pexpect.spawn(f"{protostar_bin} init")
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
def test_protostar_version_in_config_file(mocker, protostar_bin: Path):
    protostar_directory = ProtostarDirectory(protostar_bin.parent)

    version_manager = VersionManager(protostar_directory, mocker.MagicMock())
    assert version_manager.protostar_version is not None

    with open("./protostar.toml", "r+", encoding="UTF-8") as protostar_toml:
        raw_protostar_toml = protostar_toml.read()
        protostar_toml_dict = tomli.loads(raw_protostar_toml)
        version_str = protostar_toml_dict["protostar.config"]["protostar_version"]
        protostar_version = VersionManager.parse(version_str)

        assert version_manager.protostar_version == protostar_version


def test_protostar_version_in_correct_format(protostar):
    res = protostar(["--v"])

    match = re.match(r".*Cairo-lang version: (.*?)\n.*", res, flags=re.DOTALL)
    assert match, "Cairo-lang version string not found"
    assert (
        len(match.groups()) == 1
    ), f"There should be only one group, found: {match.groups()}"

    v_string = match.group(1)
    v_object = parse_version(v_string)

    # The v_object is LegacyVersion instead, when regex matching fails (as does in case of ^0.10.0)
    assert isinstance(
        v_object, Version
    ), f"Output version ({v_string}) does not meet the format requirements"
