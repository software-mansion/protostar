import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.utils.protostar_directory import ProtostarDirectory


@pytest.fixture(name="home_path")
def home_path_fixture(tmpdir: str) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="protostar_bin_dir_path")
def protostar_bin_dir_path_fixture(home_path) -> Path:
    return home_path / ".protostar" / "dist" / "protostar"


@pytest.fixture(name="protostar_in_path")
def protostar_in_path_fixture(mocker: MockerFixture, protostar_bin_dir_path: Path):
    protostar_bin_dir_path.mkdir(parents=True)
    mocker.patch("shutil.which").return_value = protostar_bin_dir_path / "protostar"


@pytest.fixture(name="protostar_not_in_path")
def protostar_not_in_path_fixture(mocker: MockerFixture):
    mocker.patch("shutil.which").return_value = None


@pytest.mark.usefixtures("protostar_in_path")
def test_protostar_binary_dir_path(protostar_bin_dir_path: Path):
    protostar_directory = ProtostarDirectory()

    assert protostar_directory.protostar_binary_dir_path == protostar_bin_dir_path


@pytest.mark.usefixtures("protostar_not_in_path")
def test_not_existing_protostar_binary_dir_path():
    protostar_directory = ProtostarDirectory()

    with pytest.raises(ProtostarDirectory.ProtostarNotInstalledException):
        # pylint: disable=pointless-statement
        protostar_directory.protostar_binary_dir_path


@pytest.mark.usefixtures("protostar_in_path")
def test_directory_root_path():
    protostar_directory = ProtostarDirectory()

    assert os.path.exists(protostar_directory.directory_root_path)


@pytest.mark.usefixtures("protostar_not_in_path")
def test_not_existing_directory_root_path():
    protostar_directory = ProtostarDirectory()

    with pytest.raises(ProtostarDirectory.ProtostarNotInstalledException):
        # pylint: disable=pointless-statement
        protostar_directory.directory_root_path
