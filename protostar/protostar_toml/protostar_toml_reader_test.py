from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_toml_exceptions import (
    NoProtostarProjectFoundException,
)
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader


@pytest.fixture(name="protostar_toml_path")
def protostar_toml_path_fixture(datadir: Path) -> Path:
    return datadir / "protostar.toml"


def test_loading_attribute(protostar_toml_path: Path):
    reader = ProtostarTOMLReader(protostar_toml_path)

    result = reader.get_attribute(
        section_name="config", attribute_name="protostar_version"
    )

    assert result == "0.2.4"


def test_loading_attribute_from_profile(protostar_toml_path: Path):
    reader = ProtostarTOMLReader(protostar_toml_path)

    non_profiled_attribute = reader.get_attribute(
        section_name="shared_command_configs", attribute_name="no-color"
    )
    assert non_profiled_attribute is False

    profiled_attribute = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no-color",
        profile_name="ci",
    )
    assert profiled_attribute is True


def test_supporting_kebab_case(protostar_toml_path: Path):
    reader = ProtostarTOMLReader(protostar_toml_path)

    result = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no-color",
    )
    assert result is False


def test_supporting_snake_case(protostar_toml_path: Path):
    reader = ProtostarTOMLReader(protostar_toml_path)

    result = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no_color",
        profile_name="ci",
    )
    assert result is True


def test_open_file_only_once(protostar_toml_path: Path, mocker: MockerFixture):
    tomli_mock = mocker.patch("protostar.protostar_toml.protostar_toml_reader.tomli")
    tomli_mock.load = mocker.MagicMock()
    tomli_mock.load.return_value = {}

    reader = ProtostarTOMLReader(protostar_toml_path)

    reader.get_attribute("_", "_")
    reader.get_attribute("__", "__")

    tomli_mock.load.assert_called_once()


def test_exception_on_file_not_found(datadir: Path):
    with pytest.raises(NoProtostarProjectFoundException):
        ProtostarTOMLReader(datadir / "_.toml").get_attribute("_", "_")


def test_returning_none_on_attribute_not_found(protostar_toml_path: Path):
    result = ProtostarTOMLReader(protostar_toml_path).get_attribute(
        "shared_command_configs", "undefined_attribute"
    )

    assert result is None


def test_retrieving_section(protostar_toml_path: Path):
    result = ProtostarTOMLReader(protostar_toml_path).get_section(
        "shared_command_configs"
    )

    assert result == {"no_color": False}


def test_returning_none_on_section_not_found(protostar_toml_path: Path):
    result = ProtostarTOMLReader(protostar_toml_path).get_section("undefined_section")

    assert result is None
