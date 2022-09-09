from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Union

from protostar.configuration_file.configuration_file import (
    ConfigurationFileContentBuilder,
    ConfigurationFileContentConfigurator,
)
from protostar.configuration_file.configuration_toml_writer import (
    ConfigurationTOMLWriter,
)


@dataclass
class SimpleConfigurationModel:
    profile_name: str
    section_name: str
    data: Dict


class ContentConfiguratorDouble(
    ConfigurationFileContentConfigurator[SimpleConfigurationModel]
):
    def create_file_content(
        self,
        content_builder: ConfigurationFileContentBuilder,
        model: SimpleConfigurationModel,
    ) -> Any:
        content_builder.set_section(
            profile_name=model.profile_name,
            section_name=model.section_name,
            data=model.data,
        )
        return content_builder.build()


@dataclass
class NonTrivialConfigurationModel:
    dependency_map: Dict[str, Union[str, Dict]]
    profile_to_dependency_map: Dict[str, Dict[str, Union[str, Dict]]]


class NonTrivialConfiguratorDouble(
    ConfigurationFileContentConfigurator[NonTrivialConfigurationModel]
):
    def create_file_content(
        self,
        content_builder: ConfigurationFileContentBuilder,
        model: NonTrivialConfigurationModel,
    ) -> Any:
        content_builder.set_section(
            section_name="dependencies", data=model.dependency_map
        )
        for profile_name, dependency_map in model.profile_to_dependency_map.items():
            content_builder.set_section(
                profile_name=profile_name,
                section_name="dependencies",
                data=dependency_map,
            )
        return content_builder.build()


def test_saving_sections_without_double_quotes(tmp_path: Path):
    toml_writer = ConfigurationTOMLWriter(
        content_configurator=ContentConfiguratorDouble()
    )
    output_file_path = tmp_path / "protostar.toml"
    model = SimpleConfigurationModel(
        profile_name="devnet", section_name="declare", data={"network": "devnet"}
    )

    toml_writer.save(
        configuration_model=model,
        filepath=output_file_path,
    )

    result = output_file_path.read_text()
    assert "[profile.devnet.declare]" in result


def test_saving_inline_table(tmp_path: Path):
    toml_writer = ConfigurationTOMLWriter(
        content_configurator=NonTrivialConfiguratorDouble()
    )
    output_file_path = tmp_path / "protostar.toml"

    toml_writer.save(
        configuration_model=NonTrivialConfigurationModel(
            dependency_map={"foo": "^1.0.0"},
            profile_to_dependency_map={"foo": {"foo": {"git": "...", "branch": "..."}}},
        ),
        filepath=output_file_path,
    )

    result = output_file_path.read_text()
    assert result == dedent(
        """\
        [dependencies]
        foo = "^1.0.0"

        [profile.foo.dependencies]
        foo = {git = "...", branch = "..."}
        """
    )
