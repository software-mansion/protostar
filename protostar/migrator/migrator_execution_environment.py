from pathlib import Path
from typing import Optional

from starknet_py.net.signer import BaseSigner

from protostar.compiler.project_compiler import ProjectCompiler
from protostar.migrator.migrator_contract_identifier_resolver import (
    MigratorContractIdentifierResolver,
)
from protostar.starknet.execution_state import ExecutionState
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.testing.environments.execution_environment import ExecutionEnvironment
from protostar.starknet.compiler.pass_managers import StarknetPassManagerFactory
from protostar.starknet.compiler.starknet_compilation import (
    CompilerConfig,
    StarknetCompiler,
)

from .migrator_cheatcodes_factory import MigratorCheatcodeFactory
from .migrator_datetime_state import MigratorDateTimeState


class MigratorExecutionEnvironment(ExecutionEnvironment[None]):
    Config = MigratorCheatcodeFactory.Config

    class Builder:
        def __init__(self, project_compiler: ProjectCompiler):
            self._project_compiler = project_compiler
            self._gateway_facade: Optional[GatewayFacade] = None
            self._migrator_datetime_state: Optional[MigratorDateTimeState] = None
            self._signer: Optional[BaseSigner] = None

        def set_gateway_facade(self, gateway_facade: GatewayFacade):
            self._gateway_facade = gateway_facade

        def set_migration_datetime_state(
            self, migrator_datetime_state: MigratorDateTimeState
        ):
            self._migrator_datetime_state = migrator_datetime_state

        def set_signer(self, signer: BaseSigner):
            self._signer = signer

        async def build(
            self,
            migration_file_path: Path,
            config: "MigratorExecutionEnvironment.Config",
        ) -> "MigratorExecutionEnvironment":
            assert self._gateway_facade is not None
            assert self._migrator_datetime_state is not None

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
            starknet = await ForkableStarknet.empty()
            contract = await starknet.deploy(contract_class=contract_class)

            state = MigratorExecutionEnvironment.State(
                starknet=starknet,
                contract=contract,
                starknet_compiler=starknet_compiler,
            )

            migrator_contract_identifier_resolver = MigratorContractIdentifierResolver(
                project_compiler=self._project_compiler,
                migrator_datetime_state=self._migrator_datetime_state,
            )

            migration_cheatcode_factory = MigratorCheatcodeFactory(
                starknet_compiler=starknet_compiler,
                gateway_facade=self._gateway_facade,
                migrator_contract_identifier_resolver=migrator_contract_identifier_resolver,
                config=config,
                signer=self._signer,
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

    async def execute(
        self,
        function_name: str,
    ) -> None:

        self.set_cheatcodes(self.cheatcode_factory)
        await self.perform_execute(function_name)
