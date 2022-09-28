from pathlib import Path
from typing import Optional

from protostar.protostar_exception import ProtostarException
from protostar.self import ProtostarVersionProviderProtocol

from .configuration_file import ConfigurationFile
from .configuration_file_v1 import ConfigurationFileV1
from .configuration_file_v2 import (
    ConfigurationFileV2,
    ConfigurationFileV2ContentConfigurator,
    ConfigurationFileV2Model,
)


class ConfigurationFileMigrator:
    def __init__(
        self,
        current_configuration_file: Optional[ConfigurationFile],
        content_configurator: ConfigurationFileV2ContentConfigurator,
        protostar_version_provider: ProtostarVersionProviderProtocol,
    ) -> None:
        self._current_configuration_file = current_configuration_file
        self._content_configurator = content_configurator
        self._protostar_version_provider = protostar_version_provider

    def run(self) -> None:
        if self._current_configuration_file is None:
            raise ConfigurationFileNotFoundException()
        if isinstance(self._current_configuration_file, ConfigurationFileV2):
            raise ConfigurationFileAlreadyMigratedException()
        assert isinstance(self._current_configuration_file, ConfigurationFileV1)
        v1_model = self._current_configuration_file.read()
        v2_model = ConfigurationFileV2Model.from_v1(
            v1_model,
            protostar_version=str(
                self._protostar_version_provider.get_protostar_version()
            ),
        )
        configuration_file_path: Path = self._current_configuration_file.get_filepath()
        backup_file_path = configuration_file_path.rename(
            configuration_file_path.parent
            / f"{configuration_file_path.stem}_backup.{configuration_file_path.suffix}"
        )
        try:
            file_content = self._content_configurator.create_file_content(v2_model)
            (
                configuration_file_path.parent
                / f"{configuration_file_path.stem}.{self._content_configurator.get_file_extension()}"
            ).write_text(file_content)
            backup_file_path.unlink()
        # pylint: disable=broad-except
        except Exception as ex:
            backup_file_path.rename(configuration_file_path)
            raise ConfigurationFileMigrationFailed(ex) from ex


class ConfigurationFileNotFoundException(ProtostarException):
    def __init__(self) -> None:
        super().__init__("No configuration file was found.")


class ConfigurationFileAlreadyMigratedException(ProtostarException):
    def __init__(self) -> None:
        super().__init__("Configuration file is already migrated.")


class ConfigurationFileMigrationFailed(ProtostarException):
    def __init__(self, ex: Exception) -> None:
        super().__init__("Configuration file migration failed.", details=str(ex))
