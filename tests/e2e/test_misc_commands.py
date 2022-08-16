# pylint: disable=redefined-outer-name
import subprocess
from os import listdir
from pathlib import Path

import pexpect
import pytest
import tomli

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


def test_init_existing(protostar_bin_path: Path):
    child = pexpect.spawn(f"{protostar_bin_path} init --existing")
    child.expect("libraries directory *", timeout=10)
    child.sendline("lib_test")
    child.expect(pexpect.EOF)
    dirs = listdir(".")

    assert "protostar.toml" in dirs
    assert "lib_test" in dirs
    assert ".git" in dirs


def test_init_ask_existing(protostar_bin_path: Path):
    open(Path() / "example.cairo", "a", encoding="utf-8").close()

    child = pexpect.spawn(f"{protostar_bin_path} init")
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
def test_protostar_version_in_config_file(mocker, protostar_bin_path: Path):
    version_manager = VersionManager(
        ProtostarDirectory(protostar_bin_path.parent), mocker.MagicMock()
    )
    assert version_manager.protostar_version is not None

    with open("./protostar.toml", "r+", encoding="UTF-8") as protostar_toml:
        raw_protostar_toml = protostar_toml.read()
        protostar_toml_dict = tomli.loads(raw_protostar_toml)
        version_str = protostar_toml_dict["protostar.config"]["protostar_version"]
        protostar_version = VersionManager.parse(version_str)

        assert version_manager.protostar_version == protostar_version


@pytest.mark.usefixtures("init")
@pytest.mark.parametrize("protostar_version", ["0.3.0"])
@pytest.mark.parametrize("protostar_toml_protostar_version", ["0.2.8"])
@pytest.mark.parametrize("last_supported_protostar_toml_version", ["0.2.9"])
@pytest.mark.parametrize("command", ["build", "install", "test"])
def test_protostar_asserts_version_compatibility(protostar, command):
    with pytest.raises(subprocess.CalledProcessError) as error:
        protostar([command])

    assert "is not compatible with provided protostar.toml" in str(error.value.output)


@pytest.mark.usefixtures("init")
@pytest.mark.parametrize("protostar_version", ["0.4.0"])
@pytest.mark.parametrize("protostar_toml_protostar_version", ["0.3.0"])
@pytest.mark.parametrize("last_supported_protostar_toml_version", ["0.3.0"])
@pytest.mark.parametrize("command", ["build", "install", "test"])
def test_protostar_passes_version_check_on_compatible_v(protostar, command):
    protostar([command])
