from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from protostar.protostar_exception import ProtostarException
from tests.conftest import create_file_structure

from .configuration_file_factory import ConfigurationFileFactory
from .configuration_file_v1 import ConfigurationFileV1
from .configuration_file_v2 import ConfigurationFileV2
from .conftest import PROTOSTAR_TOML_V1_CONTENT, PROTOSTAR_TOML_V2_CONTENT


def test_not_finding_configuration_file(mocker: MockerFixture):
    configuration_file_factory = ConfigurationFileFactory(
        cwd=Path(), command_names_provider=mocker.MagicMock()
    )

    configuration_file = configuration_file_factory.create()

    assert configuration_file is None


def test_creating_configuration_file_v1_from_subdirectory(
    tmp_path: Path, mocker: MockerFixture
):
    create_file_structure(
        root_path=tmp_path,
        file_structure_schema={
            "protostar.toml": PROTOSTAR_TOML_V1_CONTENT,
            "src": {},
        },
    )
    configuration_file_factory = ConfigurationFileFactory(
        cwd=tmp_path / "src", command_names_provider=mocker.MagicMock()
    )

    configuration_file_v1 = configuration_file_factory.create()

    assert isinstance(configuration_file_v1, ConfigurationFileV1)


def test_creating_configuration_file_v2_from_subdirectory(
    tmp_path: Path, mocker: MockerFixture
):
    (tmp_path / "protostar.toml").write_text(PROTOSTAR_TOML_V2_CONTENT)
    configuration_file_factory = ConfigurationFileFactory(
        cwd=tmp_path, command_names_provider=mocker.MagicMock()
    )

    configuration_file_v2 = configuration_file_factory.create()

    assert isinstance(configuration_file_v2, ConfigurationFileV2)


def test_not_detecting_configuration_file(tmp_path: Path, mocker: MockerFixture):
    (tmp_path / "protostar.toml").write_text("")
    configuration_file_factory = ConfigurationFileFactory(
        cwd=tmp_path, command_names_provider=mocker.MagicMock()
    )

    with pytest.raises(ProtostarException, match="protostar-version"):
        configuration_file_factory.create()


def test_handling_parsing_error(tmp_path: Path, mocker: MockerFixture):
    (tmp_path / "protostar.toml").write_text("[project")
    configuration_file_factory = ConfigurationFileFactory(
        cwd=tmp_path, command_names_provider=mocker.MagicMock()
    )

    with pytest.raises(
        ProtostarException, match="Couldn't parse the configuration file"
    ):
        configuration_file_factory.create()
