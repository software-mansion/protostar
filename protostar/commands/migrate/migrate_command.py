from pathlib import Path
from typing import List, Optional

from protostar.cli import Command
from protostar.migrator import Migrator
from protostar.migrator.migrator_cheatcodes_factory import MigratorCheatcodeFactory
from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.starknet_gateway import NetworkConfig
from protostar.utils.compiler.pass_managers import StarknetPassManagerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


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
        migrator_builder: Migrator.Builder,
        migrator_execution_env_builder: MigratorExecutionEnvironment.Builder,
        migrator_cheatcode_factory: MigratorCheatcodeFactory,
    ) -> None:
        super().__init__()
        self._migrator_builder = migrator_builder
        self._migrator_execution_env_builder = migrator_execution_env_builder
        self._migrator_cheatcode_factory = migrator_cheatcode_factory

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
        await self.migrate(contract_path=args.path, rollback=args.down)

    async def migrate(self, contract_path: Path, rollback: bool):
        compiler_config = CompilerConfig(disable_hint_validation=True, include_paths=[])
        starknet_compiler = StarknetCompiler(
            pass_manager_factory=StarknetPassManagerFactory,
            config=compiler_config,
        )
        contract_class = starknet_compiler.compile_contract(
            contract_path, add_debug_info=False
        )
        (starknet, contract) = await ForkableStarknet.from_contract_class(
            contract_class
        )

        self._migrator_execution_env_builder.set_migrator_execution_environment_state(
            MigratorExecutionEnvironment.State(
                starknet=starknet,
                contract=contract,
                starknet_compiler=starknet_compiler,
            )
        )
        self._migrator_cheatcode_factory.set_starknet_compiler(starknet_compiler)
        self._migrator_execution_env_builder.set_migration_cheatcode_factory(
            self._migrator_cheatcode_factory
        )
        execution_environment = await self._migrator_execution_env_builder.build()

        self._migrator_builder.set_migrator_execution_environment(execution_environment)
        migrator = self._migrator_builder.build()

        await migrator.run(
            mode="down" if rollback else "up",
        )
