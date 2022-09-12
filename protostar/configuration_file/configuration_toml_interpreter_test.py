from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from .configuration_toml_interpreter import (
    ConfigurationTOMLInterpreter,
    NoProtostarProjectFoundException,
)


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture() -> str:
    return """\
    ["protostar.config"]
    protostar_version = "0.2.4"

    ["protostar.project"]
    libs_path = "lib"

    ["protostar.contracts"]
    main = [
    "./src/main.cairo",
    ]

    ["protostar.shared_command_configs"]
    no_color = false

    ["profile.ci.protostar.shared_command_configs"]
    no-color = true

    ["project"]
    lib_path = "./foo"

    ["profiler.abc"]
    foo = 123
    """


@pytest.fixture(name="protostar_toml_path")
def protostar_toml_path_fixture(tmp_path: Path, protostar_toml_content: str) -> Path:
    protostar_toml_path = tmp_path / "protostar.toml"
    protostar_toml_path.write_text(protostar_toml_content)
    return protostar_toml_path


def test_loading_attribute(protostar_toml_path: Path):
    reader = ConfigurationTOMLInterpreter(protostar_toml_path)

    result = reader.get_attribute(
        section_name="config",
        attribute_name="protostar_version",
        section_namespace="protostar",
    )

    assert result == "0.2.4"


def test_loading_attribute_when_section_namespace_is_not_provided(
    protostar_toml_path: Path,
):
    reader = ConfigurationTOMLInterpreter(protostar_toml_path)

    result = reader.get_attribute(
        section_name="project",
        attribute_name="lib_path",
    )

    assert result == "./foo"


def test_loading_attribute_from_profile(protostar_toml_path: Path):
    reader = ConfigurationTOMLInterpreter(protostar_toml_path)

    non_profiled_attribute = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no_color",
        section_namespace="protostar",
    )
    assert non_profiled_attribute is False

    profiled_attribute = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no-color",
        profile_name="ci",
        section_namespace="protostar",
    )
    assert profiled_attribute is True


def test_attribute_casing_sensitivity(protostar_toml_path: Path):
    reader = ConfigurationTOMLInterpreter(protostar_toml_path)

    result = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no_color",
        profile_name="ci",
        section_namespace="protostar",
    )
    result2 = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no-color",
        section_namespace="protostar",
    )
    assert result is None
    assert result2 is None


def test_ignoring_attribute_casing(protostar_toml_path: Path):
    reader = ConfigurationTOMLInterpreter(
        protostar_toml_path, ignore_attribute_casing=True
    )

    result = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no_color",
        profile_name="ci",
        section_namespace="protostar",
    )
    result2 = reader.get_attribute(
        section_name="shared_command_configs",
        attribute_name="no-color",
        section_namespace="protostar",
    )
    assert result is True
    assert result2 is False


def test_open_file_only_once(protostar_toml_path: Path, mocker: MockerFixture):
    tomli_mock = mocker.patch(
        "protostar.configuration_file.configuration_toml_reader.tomli"
    )
    tomli_mock.load = mocker.MagicMock()
    tomli_mock.load.return_value = {}

    reader = ConfigurationTOMLInterpreter(protostar_toml_path)

    reader.get_attribute("_", "_", section_namespace="protostar")
    reader.get_attribute("__", "__", section_namespace="protostar")

    tomli_mock.load.assert_called_once()


def test_exception_on_file_not_found(datadir: Path):
    with pytest.raises(NoProtostarProjectFoundException):
        ConfigurationTOMLInterpreter(datadir / "_.toml").get_attribute(
            "_", "_", section_namespace="protostar"
        )


def test_returning_none_on_attribute_not_found(protostar_toml_path: Path):
    result = ConfigurationTOMLInterpreter(protostar_toml_path).get_attribute(
        "shared_command_configs", "undefined_attribute"
    )

    assert result is None


def test_retrieving_section(protostar_toml_path: Path):
    result = ConfigurationTOMLInterpreter(protostar_toml_path).get_section(
        "shared_command_configs", section_namespace="protostar"
    )

    assert result == {"no_color": False}


def test_returning_none_on_section_not_found(protostar_toml_path: Path):
    result = ConfigurationTOMLInterpreter(protostar_toml_path).get_section(
        "undefined_section"
    )

    assert result is None


def test_extracting_profile_names(protostar_toml_path: Path):
    result = ConfigurationTOMLInterpreter(protostar_toml_path).get_profile_names()

    assert result == ["ci"]


def test_section_starting_with_profile(
    protostar_toml_path: Path,
):
    result = ConfigurationTOMLInterpreter(protostar_toml_path).get_profile_names()

    assert "abc" not in result
