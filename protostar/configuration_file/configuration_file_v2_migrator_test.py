from pathlib import Path
from typing import Optional, Tuple

from protostar.configuration_file.configuration_file import ConfigurationFile
from protostar.self.conftest import ProtostarVersionProviderDouble
from tests.conftest import create_file_structure

from .configuration_file_factory import ConfigurationFileFactory
from .configuration_file_v1 import ConfigurationFileV1
from .configuration_file_v2 import (
    ConfigurationFileV2,
    ConfigurationFileV2ContentConfigurator,
)
from .configuration_file_v2_migrator import ConfigurationFileMigrator
from .configuration_toml_content_builder import ConfigurationTOMLContentBuilder
from .conftest import PROTOSTAR_TOML_V1_CONTENT, CommandNamesProviderTestDouble


def migrate(
    cwd: Path,
) -> Tuple[Optional[ConfigurationFile], Optional[ConfigurationFile]]:
    configuration_file_factory = ConfigurationFileFactory(
        cwd=cwd,
        command_names_provider=CommandNamesProviderTestDouble(command_names=[]),
    )
    configuration_file_before = configuration_file_factory.create()
    assert configuration_file_before is not None
    configuration_file_v2_migrator = ConfigurationFileMigrator(
        current_configuration_file=configuration_file_before,
        content_configurator=ConfigurationFileV2ContentConfigurator(
            content_builder=ConfigurationTOMLContentBuilder()
        ),
        protostar_version_provider=ProtostarVersionProviderDouble("9.9.9"),
    )

    configuration_file_v2_migrator.run()

    configuration_file_after = configuration_file_factory.create()

    return (configuration_file_before, configuration_file_after)


def test_happy_case(tmp_path: Path):
    create_file_structure(tmp_path, {"protostar.toml": PROTOSTAR_TOML_V1_CONTENT})

    (before, after) = migrate(tmp_path)

    assert isinstance(before, ConfigurationFileV1)
    assert isinstance(after, ConfigurationFileV2)
