from starkware.starknet.services.api.contract_class import ContractClass

from protostar.commands.migrate.migrator_execution_environment import \
    MigratorExecutionEnvironment
from protostar.utils.starknet_compilation import StarknetCompiler


class Migrator:
    def __init__(self, starknet_compiler: StarknetCompiler) -> None:
        self._starknet_compiler = starknet_compiler

    async def create_migration_env(
        self, contract_class: ContractClass
    ) -> MigratorExecutionEnvironment:
        return await MigratorExecutionEnvironment.create(
            starknet_compiler=self._starknet_compiler, contract_class=contract_class
        )

    def up(self):
        # prepare
        # compile it
        # create env
        # invoke up
        # save_the_file
        pass
