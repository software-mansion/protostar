import dataclasses
from dataclasses import dataclass

from starkware.starknet.testing.contract import StarknetContract
from typing_extensions import Self

from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.utils.starknet_compilation import StarknetCompiler


@dataclass
class ExecutionState:
    starknet: ForkableStarknet
    contract: StarknetContract
    starknet_compiler: StarknetCompiler

    def fork(self) -> Self:
        starknet_fork = self.starknet.fork()
        return dataclasses.replace(
            self,
            starknet=starknet_fork,
            contract=starknet_fork.copy_and_adapt_contract(self.contract),
        )
