from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.cli.network_command_mixin import NetworkCommandMixin
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig
from protostar.utils.input_requester import InputRequester
from protostar.utils.log_color_provider import LogColorProvider


class MigrateCommand(Command, NetworkCommandMixin):
    def __init__(
        self,
        migrator_builder: Migrator.Builder,
        logger: Logger,
        log_color_provider: LogColorProvider,
        requester: InputRequester,
    ) -> None:
        super().__init__()
        self._migrator_builder = migrator_builder
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._requester = requester

    @property
    def name(self) -> str:
        return "migrate"

    @property
    def description(self) -> str:
        return "Run migration file."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="path",
                description="Path to the migration file.",
                type="path",
                is_required=True,
                is_positional=True,
            ),
            Command.Argument(
                name="output-dir",
                description="Migration output directory.",
                type="path",
            ),
            Command.Argument(
                name="rollback",
                description="Run `rollback` function in the migration script.",
                type="bool",
            ),
            Command.Argument(
                name="no-confirm",
                description="Skip confirming building the project.",
                type="bool",
            ),
        ]

    async def run(self, args):
        await self.migrate(
            migration_file_path=args.path,
            rollback=args.rollback,
            network_config=self.get_network_config(args),
            network=args.network or args.gateway_url,
            output_dir_path=args.output_dir,
            no_confirm=args.no_confirm,
        )

    # pylint: disable=too-many-arguments
    async def migrate(
        self,
        migration_file_path: Path,
        rollback: bool,
        network: Optional[str],
        network_config: NetworkConfig,
        output_dir_path: Optional[Path],
        no_confirm: bool,
    ):
        # mitigates the risk of running migrate on an outdated project
        should_confirm = not no_confirm
        if should_confirm and not self._requester.confirm(
            "Did you build the project before running this command?"
        ):
            self._logger.info("Please run `protostar build`")
            self._logger.info("Migration cancelled")
            return

        self._migrator_builder.set_logger(self._logger, self._log_color_provider)
        self._migrator_builder.set_network(network)
        migrator = await self._migrator_builder.build(migration_file_path)

        try:
            migrator_history = await migrator.run(rollback)

            if output_dir_path:
                migrator.save_history(
                    migrator_history,
                    migration_file_basename=Path(migration_file_path).stem,
                    output_dir_path=output_dir_path,
                )
            self._logger.info("Migration completed")
        except CheatcodeException as ex:
            raise ProtostarException(str(ex)) from ex
