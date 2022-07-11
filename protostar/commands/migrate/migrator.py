from pathlib import Path

from starkware.starknet.services.api.contract_class import ContractClass
from typing_extensions import Literal

from protostar.commands.migrate.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.utils.starknet_compilation import StarknetCompiler


class Migrator:
    def __init__(self, starknet_compiler: StarknetCompiler) -> None:
        self._starknet_compiler = starknet_compiler

    async def run(self, mode: Literal["up", "down"], migration_path: Path):
        assert mode in ("up", "down")
        contract = self._compile_contract(migration_path)
        env = await self._create_migration_env(contract)
        await env.invoke(mode)
        # TODO: save the results

    def _compile_contract(self, path: Path) -> ContractClass:
        return self._starknet_compiler.compile_contract(path, add_debug_info=True)

    async def _create_migration_env(
        self, contract_class: ContractClass
    ) -> MigratorExecutionEnvironment:
        # TODO: provide log stack
        return await MigratorExecutionEnvironment.create(
            starknet_compiler=self._starknet_compiler, contract_class=contract_class
        )
