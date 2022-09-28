from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Union

from .configuration_file import ConfigurationFileContentConfigurator
from .configuration_toml_content_builder import ConfigurationTOMLContentBuilder


@dataclass
class SimpleConfigurationModel:
    profile_name: str
    section_name: str
    data: dict


class ContentConfiguratorDouble(
    ConfigurationFileContentConfigurator[SimpleConfigurationModel]
):
    def create_file_content(
        self,
        model: SimpleConfigurationModel,
    ) -> Any:
        content_builder = ConfigurationTOMLContentBuilder()
        content_builder.set_section(
            profile_name=model.profile_name,
            section_name=model.section_name,
            data=model.data,
        )
        return content_builder.build()


def test_saving_sections_without_double_quotes():
    content_configurator = ContentConfiguratorDouble()

    model = SimpleConfigurationModel(
        profile_name="devnet", section_name="declare", data={"network": "devnet"}
    )

    result = content_configurator.create_file_content(
        model=model,
    )

    assert result == dedent(
        """\
        [profile.devnet.declare]
        network = "devnet"
        """
    )


def test_generating_inline_table():
    @dataclass
    class NonTrivialConfigurationModel:
        dependency_map: dict[str, Union[str, dict]]
        profile_to_dependency_map: dict[str, dict[str, Union[str, dict]]]

    builder = ConfigurationTOMLContentBuilder()
    model = NonTrivialConfigurationModel(
        dependency_map={"foo": "^1.0.0"},
        profile_to_dependency_map={"foo": {"foo": {"git": "...", "branch": "..."}}},
    )
    builder.set_section(section_name="dependencies", data=model.dependency_map)
    for profile_name, dependency_map in model.profile_to_dependency_map.items():
        builder.set_section(
            profile_name=profile_name,
            section_name="dependencies",
            data=dependency_map,
        )

    result = builder.build()

    assert result == dedent(
        """\
        [dependencies]
        foo = "^1.0.0"

        [profile.foo.dependencies]
        foo = {git = "...", branch = "..."}
        """
    )


def test_building_two_sections_with_the_same_profile():
    builder = ConfigurationTOMLContentBuilder()
    builder.set_section(profile_name="foo", section_name="bar", data={"attr": 42})
    builder.set_section(profile_name="foo", section_name="baz", data={"attr": 42})
    result = builder.build()

    assert result == dedent(
        """\
        [profile.foo.bar]
        attr = 42

        [profile.foo.baz]
        attr = 42
        """
    )
