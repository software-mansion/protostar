from typing import List, Optional

from protostar.cli import Command
from protostar.commands.deploy.network_config import NetworkConfig
from protostar.commands.migrate.migrator import Migrator


class MigrateCommand(Command):
    def __init__(self, migrator: Migrator) -> None:
        super().__init__()
        self._migrator = migrator

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
        await self._migrator.run(
            mode="down" if args.down else "up",
            migration_path=args.path,
        )
