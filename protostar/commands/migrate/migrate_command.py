from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.cli.signable_command_util import SignableCommandUtil
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import GatewayFacade
from protostar.utils.input_requester import InputRequester
from protostar.utils.log_color_provider import LogColorProvider


class MigrateCommand(Command):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        migrator_builder: Migrator.Builder,
        project_root_path: Path,
        logger: Logger,
        log_color_provider: LogColorProvider,
        requester: InputRequester,
    ) -> None:
        super().__init__()
        self._migrator_builder = migrator_builder
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._requester = requester
        self._project_root_path = project_root_path

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
            *NetworkCommandUtil.network_arguments,
            *SignableCommandUtil.signable_arguments,
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

    async def run(self, args) -> Optional[Migrator.History]:
        network_command_util = NetworkCommandUtil(args, self._logger)
        network_config = network_command_util.get_network_config()
        signable_command_util = SignableCommandUtil(args, self._logger)

        migrator_config = MigratorExecutionEnvironment.Config(
            signer=signable_command_util.get_signer(network_config)
        )
        return await self.migrate(
            migration_file_path=args.path,
            rollback=args.rollback,
            gateway_facade=GatewayFacade(
                gateway_client=network_command_util.get_gateway_client(),
                log_color_provider=self._log_color_provider,
                logger=self._logger,
                project_root_path=self._project_root_path,
            ),
            output_dir_path=args.output_dir,
            no_confirm=args.no_confirm,
            migrator_config=migrator_config,
        )

    # pylint: disable=too-many-arguments
    async def migrate(
        self,
        migration_file_path: Path,
        rollback: bool,
        gateway_facade: GatewayFacade,
        output_dir_path: Optional[Path],
        migrator_config: MigratorExecutionEnvironment.Config,
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

        self._migrator_builder.set_migration_execution_environment_config(
            migrator_config
        )
        self._migrator_builder.set_gateway_facade(gateway_facade)
        migrator = await self._migrator_builder.build(migration_file_path)

        try:
            migrator_history = await migrator.run(rollback)

            if output_dir_path:
                migrator.save_history(
                    migrator_history,
                    output_dir_relative_path=output_dir_path,
                )
            self._logger.info("Migration completed")

            return migrator_history
        except CheatcodeException as ex:
            raise ProtostarException(str(ex)) from ex
