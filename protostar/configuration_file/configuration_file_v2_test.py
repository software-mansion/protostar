from pathlib import Path

import pytest

from protostar.utils.protostar_directory import VersionManager

from .configuration_file import ConfigurationFile
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

    [contracts]
    foo = [
    "./src/foo.cairo",
    ]
    bar = [
    "./src/bar.cairo",
    ]
    """


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(tmp_path: Path):
    return tmp_path


@pytest.fixture(name="configuration_file")
def configuration_file_fixture(project_root_path: Path, protostar_toml_content: str):
    protostar_toml_path = project_root_path / "protostar.toml"
    protostar_toml_path.write_text(protostar_toml_content)
    configuration_toml_reader = ConfigurationTOMLReader(path=protostar_toml_path)
    return ConfigurationFileV2(
        project_root_path=project_root_path,
        configuration_toml_reader=configuration_toml_reader,
    )


def test_retrieving_min_protostar_version(configuration_file: ConfigurationFile):
    min_protostar_version = configuration_file.get_min_protostar_version()

    assert min_protostar_version == VersionManager.parse("9.9.9")


def test_retrieving_contract_names(configuration_file: ConfigurationFile):
    contract_names = configuration_file.get_contract_names()

    assert contract_names == ["foo", "bar"]


def test_retrieving_contract_source_paths(
    configuration_file: ConfigurationFile, project_root_path: Path
):
    paths = configuration_file.get_contract_source_paths(contract_name="foo")

    assert paths == [
        (project_root_path / "./src/foo.cairo").resolve(),
        (project_root_path / "./src/bar.cairo").resolve(),
    ]
