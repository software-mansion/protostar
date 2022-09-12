import pytest

from .configuration_toml_interpreter import ConfigurationTOMLInterpreter


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        [ns.section]
        attr = "attr_val"
        """,
    ),
)
def test_getting_attribute(protostar_toml_content: str):
    interpreter = ConfigurationTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_attribute(
        section_namespace="ns", section_name="section", attribute_name="attr"
    )

    assert result == "attr_val"


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        [section]
        attr = "attr_val"
        """,
    ),
)
def test_getting_attribute_without_section_namespace(protostar_toml_content: str):
    interpreter = ConfigurationTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_attribute(section_name="section", attribute_name="attr")

    assert result == "attr_val"


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        [ns.section]
        attr = "attr_val"
        """,
    ),
)
def test_getting_section(protostar_toml_content: str):
    interpreter = ConfigurationTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_section(section_namespace="ns", section_name="section")

    assert result is not None
    assert result["attr"] == "attr_val"


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["ns.section"]
        attr = "attr_val"
        """,
    ),
)
def test_not_ignoring_section_in_quotes(protostar_toml_content: str):
    interpreter = ConfigurationTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_section(section_namespace="ns", section_name="section")

    assert result is None


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        [profile.profile_name_1]
        attr = "overwritten_attr_val"

        [profile.profile_name_2]
        attr = "overwritten_attr_val"
        """,
    ),
)
def test_getting_profile_names(protostar_toml_content: str):
    interpreter = ConfigurationTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_profile_names()

    assert result == ["profile_name_1", "profile_name_2"]


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        [profiler.section_name]
        attr = "overwritten_attr_val"
        """,
    ),
)
def test_section_starting_with_profile(
    protostar_toml_content: str,
):
    interpreter = ConfigurationTOMLInterpreter(protostar_toml_content)

    result = interpreter.get_profile_names()

    assert "section_name" not in result


def test_returning_none_on_attribute_not_found():
    interpreter = ConfigurationTOMLInterpreter("")

    result = interpreter.get_attribute("foo", "undefined_attribute")

    assert result is None


def test_returning_none_on_section_not_found():
    interpreter = ConfigurationTOMLInterpreter("")

    result = interpreter.get_section(section_name="")

    assert result is None
