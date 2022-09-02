from pathlib import Path

from conftest import generate_folder_structure

from .configuration_file_factory import ConfigurationFileFactory
from .configuration_file_v1 import ConfigurationFileV1


def test_not_finding_protostar_toml(tmp_path: Path):
    factory = ConfigurationFileFactory()

    configuration_file = factory.create_configuration_file(cwd=tmp_path)

    assert configuration_file is None


def test_creating_configuration_file_v1(tmp_path: Path):
    protostar_toml_path = tmp_path / "protostar.toml"
    protostar_toml_path.write_text(
        """
        ["protostar.config"]
        protostar_version = 0.3.0
        """
    )
    factory = ConfigurationFileFactory()

    configuration_file = factory.create_configuration_file()

    assert isinstance(configuration_file, ConfigurationFileV1) is None
