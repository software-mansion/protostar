import logging
from argparse import Namespace
from typing import Optional

from protostar.cli import ProtostarCommand
from protostar.configuration_file import ConfigurationFileMigratorProtocol


class MigrateConfigurationFileCommand(ProtostarCommand):
    NAME = "migrate-configuration-file"

    def __init__(
        self,
        configuration_file_migrator: ConfigurationFileMigratorProtocol,
    ) -> None:
        super().__init__()
        self._configuration_file_migrator = configuration_file_migrator

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def description(self) -> str:
        return "Migrate protostar.toml V1 to V2."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return []

    async def run(self, args: Namespace) -> None:
        self._configuration_file_migrator.run()
        logging.info("The configuration file was migrated successfully.")
