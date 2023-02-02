import dataclasses
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from starknet_py.net.client_models import ContractClass
from starkware.starknet.testing.contract import StarknetContract
from typing_extensions import Self

from protostar.compiler import ProjectCompiler
from protostar.starknet import Address
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.testing.starkware.test_execution_state import TestExecutionState
from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_config import TestConfig
from protostar.testing.test_context import TestContext
from protostar.testing.test_output_recorder import OutputRecorder
from protostar.testing.test_suite import TestCase


@dataclass
class ContractBasedTestExecutionState(TestExecutionState):
    contract: StarknetContract
    starknet: ForkableStarknet

    def fork(self) -> Self:
        return dataclasses.replace(
            self,
            context=deepcopy(self.context),
            config=deepcopy(self.config),
            output_recorder=self.output_recorder.fork(),
            stopwatch=self.stopwatch.fork(),
            starknet=self.starknet.fork(),
            contract=self.starknet.copy_and_adapt_contract(self.contract),
        )

    def determine_test_mode(self, test_case: TestCase):
        self.config.determine_mode_from_contract(
            test_case=test_case,
            contract=self.contract,
        )

    @classmethod
    async def from_test_suite_definition(
        cls,
        contract_path: Path,
        test_suite_definition: ContractClass,
        test_config: TestConfig,
        project_compiler: ProjectCompiler,
    ) -> Self:
        starknet = await ForkableStarknet.empty()
        stopwatch = Stopwatch()
        output_recorder = OutputRecorder()
        context = TestContext()

        contract = await starknet.deploy(contract_class=test_suite_definition)
        assert test_suite_definition.abi is not None
        starknet.cheatable_state.cheatable_state.class_hash_to_contract_abi_map[
            0
        ] = test_suite_definition.abi
        starknet.cheatable_state.cheatable_state.class_hash_to_contract_path_map[
            0
        ] = contract_path
        starknet.cheatable_state.cheatable_state.contract_address_to_class_hash_map[
            Address(contract.contract_address)
        ] = 0

        return cls(
            contract=contract,
            starknet=starknet,
            stopwatch=stopwatch,
            output_recorder=output_recorder,
            context=context,
            config=test_config,
            project_compiler=project_compiler,
        )
