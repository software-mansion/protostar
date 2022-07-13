import dataclasses
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from typing_extensions import Self

from protostar.commands.test.test_context import TestContext
from protostar.starknet.execution_state import ExecutionState
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.utils.starknet_compilation import StarknetCompiler


@dataclass
class TestExecutionState(ExecutionState):
    context: TestContext

    @classmethod
    async def from_test_suite_definition(
        cls,
        starknet_compiler: StarknetCompiler,
        test_suite_definition: ContractClass,

    ) -> Self:
        starknet = await ForkableStarknet.empty()
        contract = await starknet.deploy(contract_class=test_suite_definition)

        return cls(
            starknet=starknet,
            contract=contract,
            starknet_compiler=starknet_compiler,
            context=TestContext(),
        )

    def fork(self) -> Self:
        return dataclasses.replace(super().fork(), context=deepcopy(self.context))
