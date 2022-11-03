# pylint: disable=redefined-outer-name
import re
from os import listdir
from pathlib import Path

import pexpect
import pytest
from packaging.version import Version
from packaging.version import parse as parse_version

from protostar.configuration_file import ConfigurationFileFactory, ConfigurationFileV2
from tests.e2e.conftest import ProjectInitializer, ProtostarFixture


def test_help(protostar: ProtostarFixture):
    result = protostar(["--help"])
    assert "usage:" in result


def test_versions(protostar: ProtostarFixture):
    result = protostar(["-v"])
    assert "Protostar" in result
    assert "Cairo-lang" in result


def test_init(init_project: ProjectInitializer, project_name: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"./{project_name}")

    init_project()

    dirs = listdir(project_name)

    assert "protostar.toml" in dirs
    assert ".git" in dirs


def test_init_existing(protostar_bin: Path):
    child = pexpect.spawn(f"{protostar_bin} init --existing")
    child.expect(pexpect.EOF)
    dirs = listdir(".")

    assert "protostar.toml" in dirs
    assert ".git" in dirs


def test_init_ask_existing(protostar_bin: Path):
    open(Path() / "example.cairo", "a", encoding="utf-8").close()

    child = pexpect.spawn(f"{protostar_bin} init")
    child.expect("Your current directory.*", timeout=10)
    child.sendline("y")
    child.expect(pexpect.EOF)

    dirs = listdir(".")
    assert "protostar.toml" in dirs
    assert ".git" in dirs


@pytest.mark.usefixtures("init")
def test_creating_configuration_file_v2():
    configuration_file = ConfigurationFileFactory(cwd=Path().resolve()).create()

    assert isinstance(configuration_file, ConfigurationFileV2)
    assert configuration_file.get_declared_protostar_version() is not None


def test_protostar_version_in_correct_format(protostar: ProtostarFixture):
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
