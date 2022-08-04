# pylint: disable=redefined-outer-name
import subprocess
from os import listdir, path
from pathlib import Path

import pexpect
import pytest
import tomli
from packaging.version import Version

from protostar.protostar_toml import (
    ProtostarContractsSection,
    ProtostarConfigSection,
    ProtostarProjectSection,
)
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
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


@pytest.mark.usefixtures("init")
@pytest.mark.parametrize("declared_protostar_version", ["0.3.0"])
@pytest.mark.parametrize("breaking_protostar_versions", [["0.1.0", "1000.0.0"]])
def test_protostar_asserts_version_compatibility(protostar):
    toml_file_path = Path() / "protostar.toml"
    reader = ProtostarTOMLReader(toml_file_path)

    config_section = ProtostarConfigSection.load(reader)
    project_section = ProtostarProjectSection.load(reader)
    contracts_section = ProtostarContractsSection.load(reader)

    config_section.protostar_version = Version("0.1.0")
    ProtostarTOMLWriter().save(
        toml_file_path,
        config_section,
        project_section,
        contracts_section,
    )
    with pytest.raises(subprocess.CalledProcessError) as error:
        protostar(["build"])

    assert "You are running a higher version of protostar" in str(error.value.stdout)

    config_section.protostar_version = Version("1000.0.0")
    ProtostarTOMLWriter().save(
        toml_file_path,
        config_section,
        project_section,
        contracts_section,
    )

    with pytest.raises(subprocess.CalledProcessError) as error:
        protostar(["build"])

    assert "You are running a lower version of protostar" in str(error.value.stdout)
