from argparse import Namespace
from logging import Logger
from pathlib import Path
from typing import Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer import BaseSigner

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.cli.signable_command_util import SignableCommandUtil
from protostar.commands.build_command import BuildCommand
from protostar.io.input_requester import InputRequester
from protostar.io.log_color_provider import LogColorProvider
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_exception import ProtostarException
from protostar.starknet import CheatcodeException
from protostar.starknet_gateway.gateway_facade_factory import GatewayFacadeFactory


class MigrateCommand(ProtostarCommand):
    def __init__(
        self,
        migrator_builder: Migrator.Builder,
        logger: Logger,
        log_color_provider: LogColorProvider,
        requester: InputRequester,
        gateway_facade_factory: GatewayFacadeFactory,
    ) -> None:
        super().__init__()
        self._migrator_builder = migrator_builder
        self._logger = logger
        self._log_color_provider = log_color_provider
        self._requester = requester
        self._gateway_facade_factory = gateway_facade_factory

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
    def arguments(self):
        return [
            *NetworkCommandUtil.network_arguments,
            *SignableCommandUtil.signable_arguments,
            ProtostarArgument(
                name="path",
                description="Path to the migration file.",
                type="path",
                is_required=True,
                is_positional=True,
            ),
            ProtostarArgument(
                name="no-confirm",
                description="Skip confirming building the project.",
                type="bool",
            ),
            ProtostarArgument(
                name="compiled-contracts-dir",
                description="A directory in which your compiled contracts are located (used for deploys and declares)",
                type="path",
                default=BuildCommand.COMPILATION_OUTPUT_ARG.default,
            ),
        ]

    async def run(self, args: Namespace) -> Optional[Migrator.History]:
        self._logger.warning(
            """\
Migrations feature is deprecated and is scheduled for removal before Cairo 1.0 release.

Declaring and deploying contracts via Protostar CLI is the recommended approach.
Alternatively, one can only build contracts with Protostar and use custom scripts using one \
of StarkNet's SDKs available.

Consult https://docs.swmansion.com/protostar/docs/tutorials/deploying for more information.
"""
        )

        network_command_util = NetworkCommandUtil(args, self._logger)
        network_config = network_command_util.get_network_config()
        signable_command_util = SignableCommandUtil(args, self._logger)
        signer = signable_command_util.get_signer(network_config)
        migrator_config = MigratorExecutionEnvironment.Config(
            account_address=args.account_address,
        )

        return await self.migrate(
            migration_file_path=args.path,
            gateway_client=network_command_util.get_gateway_client(),
            no_confirm=args.no_confirm,
            migrator_config=migrator_config,
            signer=signer,
            compiled_contracts_dir_path=args.compiled_contracts_dir,
        )

    async def migrate(
        self,
        migration_file_path: Path,
        gateway_client: GatewayClient,
        migrator_config: MigratorExecutionEnvironment.Config,
        no_confirm: bool,
        compiled_contracts_dir_path: Path,
        signer: Optional[BaseSigner] = None,
    ):
        # mitigates the risk of running migrate on an outdated project
        should_confirm = not no_confirm
        if should_confirm and not self._requester.confirm(
            "Did you build the project before running this command?"
        ):
            self._logger.info("Please run `protostar build`")
            self._logger.info("Migration cancelled")
            return

        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=gateway_client, logger=self._logger
        )

        self._migrator_builder.set_logger(self._logger, self._log_color_provider)

        self._migrator_builder.set_migration_execution_environment_config(
            migrator_config
        )

        if signer:
            self._migrator_builder.set_signer(signer)

        self._migrator_builder.set_gateway_facade(gateway_facade)
        migrator = await self._migrator_builder.build(
            migration_file_path=migration_file_path,
            compiled_contracts_dir_path=compiled_contracts_dir_path,
        )

        try:
            migrator_history = await migrator.run()
            migrator.save_history(migrator_history, migration_file_path.parent)
            self._logger.info("Migration completed")

            return migrator_history
        except CheatcodeException as ex:
            raise ProtostarException(str(ex)) from ex
