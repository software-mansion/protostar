import dataclasses
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract

from protostar.commands.test.starkware import ForkableStarknet
from protostar.commands.test.test_context import TestContext
from protostar.utils.starknet_compilation import StarknetCompiler


@dataclass
class ExecutionState:
    starknet: ForkableStarknet
    contract: StarknetContract
    starknet_compiler: StarknetCompiler
    include_paths: List[str]
    disable_hint_validation_in_external_contracts: bool
    context: TestContext = field(default_factory=TestContext)

    @classmethod
    async def from_test_suite_definition(
        cls,
        starknet_compiler: StarknetCompiler,
        test_suite_definition: ContractClass,
        disable_hint_validation_in_external_contracts: bool,
        include_paths: Optional[List[str]] = None,
    ) -> "ExecutionState":
        starknet = await ForkableStarknet.empty()
        contract = await starknet.deploy(contract_class=test_suite_definition)

        return cls(
            starknet=starknet,
            contract=contract,
            starknet_compiler=starknet_compiler,
            include_paths=include_paths or [],
            disable_hint_validation_in_external_contracts=disable_hint_validation_in_external_contracts,
        )

    def fork(self) -> "ExecutionState":
        starknet_fork = self.starknet.fork()
        return dataclasses.replace(
            self,
            starknet=starknet_fork,
            contract=starknet_fork.copy_and_adapt_contract(self.contract),
            context=deepcopy(self.context),
        )
