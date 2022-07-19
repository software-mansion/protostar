from pathlib import Path

from protostar.migrator.migrator_cheatcodes_factory import MigratorCheatcodeFactory
from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.starknet.execution_state import ExecutionState
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.utils.compiler.pass_managers import StarknetPassManagerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


class MigratorExecutionEnvironment(ExecutionEnvironment[None]):
    class Factory:
        @staticmethod
        async def build(migration_file_path: Path) -> "MigratorExecutionEnvironment":
            compiler_config = CompilerConfig(
                disable_hint_validation=True, include_paths=[]
            )
            starknet_compiler = StarknetCompiler(
                pass_manager_factory=StarknetPassManagerFactory,
                config=compiler_config,
            )
            contract_class = starknet_compiler.compile_contract(
                migration_file_path, add_debug_info=False
            )
            (starknet, contract) = await ForkableStarknet.from_contract_class(
                contract_class
            )

            state = MigratorExecutionEnvironment.State(
                starknet=starknet,
                contract=contract,
                starknet_compiler=starknet_compiler,
            )
            migration_cheatcode_factory = MigratorCheatcodeFactory(starknet_compiler)

            return MigratorExecutionEnvironment(
                state=state,
                migrator_cheatcode_factory=migration_cheatcode_factory,
            )

    class State(ExecutionState):
        pass

    def __init__(
        self, state: "State", migrator_cheatcode_factory: MigratorCheatcodeFactory
    ):
        super().__init__(state)
        self._migrator_cheatcode_factory = migrator_cheatcode_factory

    async def invoke(self, function_name: str) -> None:
        self.set_cheatcodes(self._migrator_cheatcode_factory)
        await self.perform_invoke(function_name)
