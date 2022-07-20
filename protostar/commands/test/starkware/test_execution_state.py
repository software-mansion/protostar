import dataclasses
from copy import deepcopy
from dataclasses import dataclass

from starkware.starknet.services.api.contract_class import ContractClass
from typing_extensions import Self

from protostar.commands.test.test_context import TestContext
from protostar.starknet.execution_state import ExecutionState
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.utils.starknet_compilation import StarknetCompiler
from protostar.commands.test.test_output_recorder import OutputName, OutputRecorder


@dataclass
class TestExecutionState(ExecutionState):
    context: TestContext
    output_recorder: OutputRecorder

    @classmethod
    async def from_test_suite_definition(
        cls,
        starknet_compiler: StarknetCompiler,
        test_suite_definition: ContractClass,
    ) -> Self:

        starknet = await ForkableStarknet.empty()
        contract = await starknet.deploy(contract_class=test_suite_definition)
        assert test_suite_definition.abi is not None
        starknet.cheatable_state.cheatable_carried_state.class_hash_to_contract_abi_map[
            0
        ] = test_suite_definition.abi
        starknet.cheatable_state.cheatable_carried_state.contract_address_to_class_hash_map[
            contract.contract_address
        ] = 0
        return cls(
            starknet=starknet,
            contract=contract,
            starknet_compiler=starknet_compiler,
            context=TestContext(),
            output_recorder=OutputRecorder(),
        )

    def get_output(self, name: OutputName):
        return self.output_recorder.captures[name].getvalue()

    def fork(self) -> Self:
        return dataclasses.replace(
            super().fork(),
            context=deepcopy(self.context),
            output_recorder=deepcopy(self.output_recorder),
        )
