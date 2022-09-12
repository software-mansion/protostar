from pathlib import Path

import pytest

from .configuration_toml_interpreter import ConfigurationStrictTOMLInterpreter


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture() -> str:
    return """\
    [ns.section]
    attr = "attr_val"

    ["quoted.section"]
    attr = "attr_val"

    [profile.profile_name_1]
    attr = "overwritten_attr_val"

    [profile.profile_name_2]
    attr = "overwritten_attr_val"
    """


@pytest.fixture(name="protostar_toml_path")
def protostar_toml_path_fixture(tmp_path: Path, protostar_toml_content: str) -> Path:
    protostar_toml_path = tmp_path / "protostar.toml"
    protostar_toml_path.write_text(protostar_toml_content)
    return protostar_toml_path


def test_getting_attribute(protostar_toml_content: str):
    interpreter = ConfigurationStrictTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_attribute(
        section_namespace="ns", section_name="section", attribute_name="attr"
    )

    assert result == "attr_val"


def test_getting_section(protostar_toml_content: str):
    interpreter = ConfigurationStrictTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_section(section_namespace="ns", section_name="section")

    assert result is not None
    assert result["attr"] == "attr_val"


def test_not_getting_section_in_quotes(protostar_toml_content: str):
    interpreter = ConfigurationStrictTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_section(section_namespace="quoted", section_name="section")

    assert result is None


def test_getting_profile_names(protostar_toml_content: str):
    interpreter = ConfigurationStrictTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_profile_names()

    assert result == ["profile_name_1", "profile_name_2"]
