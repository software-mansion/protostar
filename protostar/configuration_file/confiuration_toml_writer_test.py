from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from protostar.configuration_file.configuration_file import (
    ConfigurationFileContentBuilder,
    ConfigurationFileContentConfigurator,
)
from protostar.configuration_file.configuration_toml_writer import (
    ConfigurationTOMLWriter,
)


@dataclass
class ConfigurationModelDouble:
    profile_name: str
    section_name: str
    data: Dict


class ContentConfiguratorDouble(
    ConfigurationFileContentConfigurator[ConfigurationModelDouble]
):
    def create_file_content(
        self,
        content_builder: ConfigurationFileContentBuilder,
        model: ConfigurationModelDouble,
    ) -> Any:
        content_builder.set_section(
            profile_name=model.profile_name,
            section_name=model.section_name,
            data=model.data,
        )
        return content_builder.build()


def test_saving_sections_without_double_quotes(tmp_path: Path):
    toml_writer = ConfigurationTOMLWriter(
        content_configurator=ContentConfiguratorDouble()
    )
    output_file_path = tmp_path / "protostar.toml"
    model = ConfigurationModelDouble(
        profile_name="devnet", section_name="declare", data={"network": "devnet"}
    )

    toml_writer.save(
        configuration_model=model,
        filepath=output_file_path,
    )

    result = output_file_path.read_text()
    assert result is not None
    assert not '["' in result
    assert not '"]' in result
