from pathlib import Path

from tests.conftest import create_file_structure

from .configuration_file_factory import ConfigurationFileFactory
from .configuration_file_v1 import ConfigurationFileV1

PROTOSTAR_TOML_V1_CONTENT = """
["protostar.config"]
protostar_version = 0.4.0
"""


def test_not_finding_configuration_file():
    configuration_file_factory = ConfigurationFileFactory(cwd=Path())

    configuration_file = configuration_file_factory.create()

    assert configuration_file is None


def test_creating_configuration_file_v1_from_subdirectory(tmp_path: Path):
    create_file_structure(
        root_path=tmp_path,
        file_structure_schema={
            "protostar.toml": PROTOSTAR_TOML_V1_CONTENT,
            "src": {},
        },
    )
    configuration_file_factory = ConfigurationFileFactory(cwd=tmp_path / "src")

    configuration_file_v1 = configuration_file_factory.create()

    assert configuration_file_v1 is ConfigurationFileV1
