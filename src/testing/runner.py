from dataclasses import dataclass, field
from typing import List, NewType, NamedTuple

from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.starknet import Starknet

from src.starknet_compilation import compile_contract
from src.testing.collector import TestCollector

ProgramOutput = NewType("ProgramOutput", NamedTuple)


@dataclass
class TestRunner:
    failed_functions: List[ProgramOutput] = field(
        default_factory=list
    )  # TODO: Capture outputs and show at end of testing session
    succeeded_functions: List[ProgramOutput] = field(default_factory=list)

    async def run_tests_in(self, src: str):
        test_subjects = TestCollector(sources_directory=src).collect()
        for test_subject in test_subjects:
            compiled_test = compile_contract(test_subject.test_path)
            compiled_target = compile_contract(test_subject.target_path)

            await self.run_test_functions(
                test_contract=compiled_test,
                target_contract=compiled_target,
                functions=test_subject.test_functions,
            )

    async def run_test_functions(
        self,
        test_contract: ContractDefinition,
        target_contract: ContractDefinition,
        functions: List[dict],
    ):
        for function in functions:
            starknet = await Starknet.empty()
            test_contract = await starknet.deploy(contract_def=test_contract)
            target_contract = await starknet.deploy(contract_def=target_contract)

            # TODO: Invocation should probably be passed some parameters to allow for prettier stacktraces
            invocation_result = getattr(test_contract, function["name"])(
                test_contract.contract_address
            )  # TODO: Support parametric tests

            print(invocation_result)
            # TODO: Determine failures and successes
            self.succeeded_functions.append(
                # ^ if success...
                invocation_result
            )
            self.failed_functions.append(
                # ^ if failures...
                invocation_result
            )
