from pathlib import Path

import pytest

from protostar.protostar_exception import ProtostarException
from tests.conftest import create_file_structure

from .configuration_file_factory import ConfigurationFileFactory
from .configuration_file_v1 import ConfigurationFileV1
from .configuration_file_v2 import ConfigurationFileV2

PROTOSTAR_TOML_V1_CONTENT = """
["protostar.config"]
protostar_version = "0.4.0"
"""

PROTOSTAR_TOML_V2_CONTENT = """
[project]
protostar-version = "0.5.0"
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

    assert isinstance(configuration_file_v1, ConfigurationFileV1)


def test_creating_configuration_file_v2_from_subdirectory(tmp_path: Path):
    (tmp_path / "protostar.toml").write_text(PROTOSTAR_TOML_V2_CONTENT)
    configuration_file_factory = ConfigurationFileFactory(cwd=tmp_path)

    configuration_file_v2 = configuration_file_factory.create()

    assert isinstance(configuration_file_v2, ConfigurationFileV2)


def test_not_detecting_configuration_file(tmp_path: Path):
    (tmp_path / "protostar.toml").write_text("")
    configuration_file_factory = ConfigurationFileFactory(cwd=tmp_path)

    with pytest.raises(ProtostarException, match="protostar-version"):
        configuration_file_factory.create()
