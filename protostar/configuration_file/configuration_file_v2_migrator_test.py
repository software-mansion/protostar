import os
from pathlib import Path
from typing import Optional, Tuple

import pytest

from protostar.self.conftest import FakeProtostarVersionProvider
from tests.conftest import create_file_structure

from .configuration_file import ConfigurationFile, ConfigurationFileContentBuilder
from .configuration_file_factory import ConfigurationFileFactory
from .configuration_file_v1 import ConfigurationFileV1
from .configuration_file_v2 import (
    ConfigurationFileV2,
    ConfigurationFileV2ContentFactory,
)
from .configuration_file_v2_migrator import (
    ConfigurationFileAlreadyMigratedException,
    ConfigurationFileMigrationFailed,
    ConfigurationFileNotFoundException,
    ConfigurationFileV2Migrator,
)
from .configuration_toml_content_builder import ConfigurationTOMLContentBuilder
from .conftest import (
    PROTOSTAR_TOML_V1_CONTENT,
    PROTOSTAR_TOML_V2_CONTENT,
    FakeCommandNamesProvider,
)


def test_happy_case(tmp_path: Path):
    create_file_structure(tmp_path, {"protostar.toml": PROTOSTAR_TOML_V1_CONTENT})

    (before, after) = migrate(cwd=tmp_path)

    assert isinstance(before, ConfigurationFileV1)
    assert isinstance(after, ConfigurationFileV2)
    assert_file_count(tmp_path, 1)


def test_migrate_from_subdirectory(tmp_path: Path):
    create_file_structure(
        tmp_path, {"protostar.toml": PROTOSTAR_TOML_V1_CONTENT, "src": {}}
    )

    (before, after) = migrate(cwd=tmp_path / "src")

    assert isinstance(before, ConfigurationFileV1)
    assert isinstance(after, ConfigurationFileV2)
    assert_file_count(tmp_path, 1)


def test_no_configuration_file(tmp_path: Path):
    with pytest.raises(ConfigurationFileNotFoundException):
        migrate(tmp_path)

    assert_file_count(tmp_path, 0)


def test_migrating_migrated_configuration_file(tmp_path: Path):
    create_file_structure(tmp_path, {"protostar.toml": PROTOSTAR_TOML_V2_CONTENT})

    with pytest.raises(ConfigurationFileAlreadyMigratedException):
        migrate(cwd=tmp_path)

    assert (tmp_path / "protostar.toml").read_text() == PROTOSTAR_TOML_V2_CONTENT
    assert_file_count(tmp_path, 1)


def test_rollback(tmp_path: Path):
    class ConfigurationFileContentBuilderStub(ConfigurationTOMLContentBuilder):
        def build(self) -> str:
            raise Exception()

    create_file_structure(tmp_path, {"protostar.toml": PROTOSTAR_TOML_V1_CONTENT})

    with pytest.raises(ConfigurationFileMigrationFailed):
        migrate(cwd=tmp_path, content_builder=ConfigurationFileContentBuilderStub())

    assert (tmp_path / "protostar.toml").read_text() == PROTOSTAR_TOML_V1_CONTENT
    assert_file_count(tmp_path, 1)


def migrate(
    cwd: Path, content_builder: Optional[ConfigurationFileContentBuilder] = None
) -> Tuple[Optional[ConfigurationFile], Optional[ConfigurationFile]]:
    command_names_provider = FakeCommandNamesProvider(command_names=[])
    configuration_file_factory = ConfigurationFileFactory(cwd=cwd)
    configuration_file_before = configuration_file_factory.create()
    if configuration_file_before:
        configuration_file_before.set_command_names_provider(command_names_provider)
    configuration_file_v2_migrator = ConfigurationFileV2Migrator(
        current_configuration_file=configuration_file_before,
        content_factory=ConfigurationFileV2ContentFactory(
            content_builder=content_builder or ConfigurationTOMLContentBuilder()
        ),
        protostar_version_provider=FakeProtostarVersionProvider("9.9.9"),
    )

    configuration_file_v2_migrator.run()

    configuration_file_after = configuration_file_factory.create()
    if configuration_file_after:
        configuration_file_after.set_command_names_provider(command_names_provider)

    return (configuration_file_before, configuration_file_after)


def assert_file_count(path: Path, count: int):
    assert len(next(os.walk(path))[2]) == count
