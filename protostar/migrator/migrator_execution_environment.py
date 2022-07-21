from pathlib import Path

from protostar.migrator.cheatcodes.migrator_declare_cheatcode import (
    MigratorDeclareCheatcode,
)
from protostar.migrator.migrator_cheatcodes_factory import MigratorCheatcodeFactory
from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.starknet.execution_state import ExecutionState
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.compiler.pass_managers import StarknetPassManagerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


class MigratorExecutionEnvironment(ExecutionEnvironment[None]):
    Config = MigratorDeclareCheatcode.Config

    class Factory:
        def __init__(
            self,
            gateway_facade: GatewayFacade,
        ) -> None:
            self._gateway_facade = gateway_facade

        async def build(
            self,
            migration_file_path: Path,
            config: "MigratorExecutionEnvironment.Config",
        ) -> "MigratorExecutionEnvironment":
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
            migration_cheatcode_factory = MigratorCheatcodeFactory(
                starknet_compiler,
                self._gateway_facade,
                config=config,
            )

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
        self.cheatcode_factory = migrator_cheatcode_factory

    async def invoke(
        self,
        function_name: str,
    ) -> None:

        self.set_cheatcodes(self.cheatcode_factory)
        await self.perform_invoke(function_name)
