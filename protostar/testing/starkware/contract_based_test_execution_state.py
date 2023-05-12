import dataclasses
from dataclasses import dataclass
from pathlib import Path

from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
)
from starkware.starknet.testing.contract import StarknetContract
from typing_extensions import Self

from protostar.compiler import Cairo0ProjectCompiler
from protostar.compiler.project_compiler import ProjectCompiler
from protostar.starknet import Address
from protostar.testing.starkware.test_execution_state import TestExecutionState
from protostar.testing.test_config import TestConfig
from protostar.testing.test_suite import TestCase


@dataclass
class ContractBasedTestExecutionState(TestExecutionState):
    contract: StarknetContract

    def fork(self) -> Self:
        super_instance = super().fork()
        return dataclasses.replace(
            super_instance,
            contract=super_instance.starknet.copy_and_adapt_contract(self.contract),
        )

    @classmethod
    async def from_test_suite_definition(
        cls,
        contract_path: Path,
        test_suite_definition: DeprecatedCompiledClass,
        test_config: TestConfig,
        cairo0_project_compiler: Cairo0ProjectCompiler,
        project_compiler: ProjectCompiler,
    ) -> Self:
        base = await TestExecutionState.from_test_config(
            test_config, cairo0_project_compiler, project_compiler
        )
        starknet = base.starknet

        sender_address = await starknet.deploy_simple_account()
        declared_class = await starknet.deprecated_declare(
            contract_class=test_suite_definition
        )
        contract = await starknet.deploy(
            class_hash=declared_class.class_hash, sender_address=sender_address
        )
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
            starknet=base.starknet,
            stopwatch=base.stopwatch,
            output_recorder=base.output_recorder,
            context=base.context,
            config=base.config,
            cairo0_project_compiler=base.cairo0_project_compiler,
            project_compiler=base.project_compiler,
        )

    def determine_test_mode(self, test_case: TestCase):
        self.config.determine_mode(test_case=test_case, contract=self.contract)
