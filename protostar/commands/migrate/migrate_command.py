from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.migrator import Migrator
from protostar.starknet_gateway import NetworkConfig


class MigrateCommand(Command):
    """
    #### Migration
    ```cairo
    %lang starknet
    from starkware.starknet.common.syscalls import deploy
    from starkware.cairo.common.alloc import alloc

    @external
    func up{syscall_ptr : felt*}() -> (contract_address : felt):
        alloc_locals
        local class_hash
        %{ ids.class_hash = declare("./build/main.json").class_hash %}
        let (local calldata : felt*) = alloc()
        let (contract_address) = deploy(class_hash, 42, 0, calldata)

        return (contract_address)
    end
    ```
    """

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
        await self.migrate(migration_file_path=args.path, rollback=args.down)

    async def migrate(self, migration_file_path: Path, rollback: bool):
        migrator = await self._migrator_factory.build(migration_file_path)

        await migrator.run(
            mode="down" if rollback else "up",
        )
