from pathlib import Path

from protostar.configuration_file.configuration_toml_writer import (
    ConfigurationTOMLWriter,
)


def test_saving_sections_without_double_quotes(tmp_path: Path):
    writer = ConfigurationTOMLWriter(output_file_path=tmp_path / "config_file.toml")
    builder = writer.create_content_builder()
    builder.set_section(
        profile_name="devnet", section_name="declare", data={"network": "devnet"}
    )
    content = builder.build()

    output_file_path = writer.save(content)
    result = output_file_path.read_text()

    assert not '["' in result
    assert not '"]' in result
