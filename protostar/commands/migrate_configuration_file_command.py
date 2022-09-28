from logging import Logger
from typing import List, Optional

from protostar.cli import Command
from protostar.configuration_file import ConfigurationFileMigratorProtocol


class MigrateConfigurationFileCommand(Command):
    def __init__(
        self,
        logger: Logger,
        configuration_file_migrator: ConfigurationFileMigratorProtocol,
    ) -> None:
        super().__init__()
        self._logger = logger
        self._configuration_file_migrator = configuration_file_migrator

    @property
    def name(self) -> str:
        return "migrate-configuration-file"

    @property
    def description(self) -> str:
        return "Migrate protostar.toml to the new version introduced in Protostar v0.5"

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return []

    async def run(self, args) -> None:
        self._configuration_file_migrator.run()
        self._logger.info("The configuration file was migrated successfully.")
