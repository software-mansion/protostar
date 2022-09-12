import pytest

from .configuration_legacy_toml_interpreter import ConfigurationLegacyTOMLInterpreter


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["protostar.config"]
        protostar_version = "0.2.4"
        """,
    ),
)
def test_loading_attribute(protostar_toml_content: str):
    reader = ConfigurationLegacyTOMLInterpreter(protostar_toml_content)

    result = reader.get_attribute(
        section_name="config",
        attribute_name="protostar_version",
        section_namespace="protostar",
    )

    assert result == "0.2.4"


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["protostar.project"]
        libs_path = "lib"
        """,
    ),
)
def test_loading_attribute_when_section_namespace_is_not_provided(
    protostar_toml_content: str,
):
    reader = ConfigurationLegacyTOMLInterpreter(protostar_toml_content)

    result = reader.get_attribute(
        section_name="project",
        attribute_name="lib_path",
    )

    assert result == "./foo"


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["protostar.shared_command_configs"]
        no_color = false

        ["profile.ci.protostar.shared_command_configs"]
        no-color = true
        """,
    ),
)
def test_loading_attribute_from_profile(protostar_toml_content: str):
    reader = ConfigurationLegacyTOMLInterpreter(protostar_toml_content)

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


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["protostar.shared_command_configs"]
        no_color = false

        ["profile.ci.protostar.shared_command_configs"]
        no-color = true
        """,
    ),
)
def test_ignoring_attribute_casing(protostar_toml_content: str):
    reader = ConfigurationLegacyTOMLInterpreter(
        protostar_toml_content,
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


def test_returning_none_on_attribute_not_found():
    result = ConfigurationLegacyTOMLInterpreter("").get_attribute(
        "shared_command_configs", "undefined_attribute"
    )

    assert result is None


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["protostar.shared_command_configs"]
        no_color = false
        """,
    ),
)
def test_retrieving_section(protostar_toml_content: str):
    result = ConfigurationLegacyTOMLInterpreter(protostar_toml_content).get_section(
        "shared_command_configs", section_namespace="protostar"
    )

    assert result == {"no_color": False}


def test_returning_none_on_section_not_found():
    result = ConfigurationLegacyTOMLInterpreter("").get_section("undefined_section")

    assert result is None


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["profile.ci.protostar.shared_command_configs"]
        no-color = true

        ["profiler.abc"]
        foo = 123

        ["profile."]
        foo = 123
        """,
    ),
)
def test_extracting_profile_names(protostar_toml_content: str):
    result = ConfigurationLegacyTOMLInterpreter(
        protostar_toml_content
    ).get_profile_names()

    assert result == ["ci"]


@pytest.mark.parametrize(
    "protostar_toml_content",
    (
        """
        ["profiler.abc"]
        foo = 123
        """,
    ),
)
def test_section_starting_with_profile(
    protostar_toml_content: str,
):
    result = ConfigurationLegacyTOMLInterpreter(
        protostar_toml_content
    ).get_profile_names()

    assert "abc" not in result
