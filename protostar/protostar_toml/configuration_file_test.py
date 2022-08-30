# pylint: disable=unused-argument
from pathlib import Path

import pytest

from protostar.utils import VersionManager

from .configuration_file import ConfigurationFile, ConfigurationFileV1
from .io.protostar_toml_reader import ProtostarTOMLReader


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture():
    return ""


@pytest.fixture(name="protostar_toml_path")
def protostar_toml_path_fixture(protostar_toml_content: str, tmp_path: Path):
    path = tmp_path / "protostar.toml"
    path.write_text(protostar_toml_content)
    return path


@pytest.fixture(name="configuration_file")
def configuration_file_fixture(protostar_toml_path: Path):
    protostar_toml_reader = ProtostarTOMLReader(protostar_toml_path=protostar_toml_path)
    return ConfigurationFileV1(protostar_toml_reader)


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.config"]
        protostar_version = "0.1.2"
        """
    ],
)
def test_loading_min_protostar_version(
    configuration_file: ConfigurationFile, protostar_toml_content: str
):
    min_protostar_version = configuration_file.get_min_protostar_version()

    assert min_protostar_version == VersionManager.parse("0.1.2")
