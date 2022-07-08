from starkware.starknet.services.api.contract_class import ContractClass

from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.starknet.execution_state import ExecutionState
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.utils.starknet_compilation import StarknetCompiler


class MigratorExecutionEnvironment(ExecutionEnvironment[None]):
    class State(ExecutionState):
        pass

    def __init__(self, state: ExecutionState):
        super().__init__(state)

    @classmethod
    async def create(
        cls, starknet_compiler: StarknetCompiler, contract_class: ContractClass
    ) -> "MigratorExecutionEnvironment":

        starknet = await ForkableStarknet.empty()
        contract = await starknet.deploy(contract_class=contract_class)
        return cls(
            state=MigratorExecutionEnvironment.State(
                # compiler config data class?
                # builder?
            )
        )

    async def invoke(self, function_name: str) -> None:
        pass
