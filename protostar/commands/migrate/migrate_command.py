from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.migrator import Migrator
from protostar.starknet_gateway import NetworkConfig


class MigrateCommand(Command):
    def __init__(
        self,
        migrator_factory: Migrator.Factory,
    ) -> None:
        super().__init__()
        self._migrator_factory = migrator_factory

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
                description="Migration output directory",
                type="path",
            ),
            Command.Argument(
                name="down",
                description="Run `down` function in the migration script.",
                type="str",
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
        )

    # pylint: disable=too-many-arguments
    async def migrate(
        self,
        migration_file_path: Path,
        rollback: bool,
        gateway_url: Optional[str],
        network: Optional[str],
        output_dir_path: Optional[Path],
    ):
        network_config = NetworkConfig.build(gateway_url, network)

        migrator = await self._migrator_factory.build(
            migration_file_path,
            config=Migrator.Config(gateway_url=network_config.gateway_url),
        )

        result = await migrator.run(
            mode="down" if rollback else "up",
        )

        if output_dir_path:
            migrator.save_result(
                result,
                migration_file_path=migration_file_path,
                output_dir_path=output_dir_path,
            )
