from pathlib import Path

import pytest

from protostar.utils.protostar_directory import VersionManager

from .configuration_file_v2 import ConfigurationFileV2
from .configuration_toml_reader import ConfigurationTOMLReader


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture() -> str:
    return """\
    [project]
    min-protostar-version="9.9.9"
    lib-path="./lib"
    no-color=true
    network="devnet1"
    cairo-path=["bar"]

    [declare]
    network="devnet2"

    [profile.release.declare]
    network="mainnet"
    """


@pytest.fixture(name="configuration_file")
def configuration_file_fixture(tmp_path: Path, protostar_toml_content: str):
    protostar_toml_path = tmp_path / "protostar.toml"
    protostar_toml_path.write_text(protostar_toml_content)
    protostar_toml_reader = ConfigurationTOMLReader(path=protostar_toml_path)
    return ConfigurationFileV2(protostar_toml_reader)


def test_retrieving_min_protostar_version(configuration_file: ConfigurationFileV2):
    min_protostar_version = configuration_file.get_min_protostar_version()

    assert min_protostar_version == VersionManager.parse("9.9.9")
