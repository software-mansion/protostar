from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig
from protostar.utils.input_requester import InputRequester
from protostar.utils.log_color_provider import LogColorProvider


class MigrateCommand(Command):
    def __init__(
        self,
        migrator_factory: Migrator.Factory,
        logger: Logger,
        log_color_provider: LogColorProvider,
        requester: InputRequester,
    ) -> None:
        super().__init__()
        self._migrator_factory = migrator_factory
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
                name="down",
                description="Run `down` function in the migration script.",
                type="str",
            ),
            Command.Argument(
                name="no-confirm",
                description="Skip confirming building the project.",
                type="bool",
            ),
            Command.Argument(
                name="gateway-url",
                description="The URL of a StarkNet gateway. It is required unless `--network` is provided.",
                type="str",
            ),
            Command.Argument(
                name="network",
                short_name="n",
                description=(
                    "\n".join(
                        [
                            "The name of the StarkNet network.",
                            "It is required unless `--gateway-url` is provided.",
                            "",
                            "Supported StarkNet networks:",
                        ]
                        + [f"- `{n}`" for n in NetworkConfig.get_starknet_networks()]
                    )
                ),
                type="str",
            ),
        ]

    async def run(self, args):
        await self.migrate(
            migration_file_path=args.path,
            rollback=args.down,
            gateway_url=args.gateway_url,
            network=args.network,
            output_dir_path=args.output_dir,
            no_confirm=args.no_confirm,
        )

    # pylint: disable=too-many-arguments
    async def migrate(
        self,
        migration_file_path: Path,
        rollback: bool,
        gateway_url: Optional[str],
        network: Optional[str],
        output_dir_path: Optional[Path],
        no_confirm: bool,
    ):
        network_config = NetworkConfig.build(gateway_url, network)

        # mitigates the risk of running migrate on an outdated project
        should_confirm = not no_confirm
        if should_confirm and not self._requester.confirm(
            "Did you build the project before running this command?"
        ):
            self._logger.info("Migration cancelled")
            return

        self._migrator_factory.set_logger(self._logger, self._log_color_provider)

        migrator = await self._migrator_factory.build(
            migration_file_path,
            config=Migrator.Config(gateway_url=network_config.gateway_url),
        )

        try:
            result = await migrator.run(
                mode="down" if rollback else "up",
            )

            if output_dir_path:
                migrator.save_result(
                    result,
                    migration_file_basename=Path(migration_file_path).stem,
                    output_dir_path=output_dir_path,
                )
        except CheatcodeException as ex:
            raise ProtostarException(str(ex)) from ex
