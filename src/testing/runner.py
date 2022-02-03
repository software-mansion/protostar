from dataclasses import dataclass, field
from typing import List, Optional, Union

from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

from src.starknet_compilation import StarknetCompiler
from src.testing.collector import TestCollector


@dataclass
class TestRunner:
    include_paths: Optional[List[str]] = None
    failed_tests: List[Union[StarkException]] = field(default_factory=list)
    succeeded_tests: List[dict] = field(default_factory=list)

    # Logging methods
    def _case_success(self, result: dict):
        self.succeeded_tests.append(result)
        print(".", end="")

    def _case_failure(self, ex: StarkException):
        self.failed_tests.append(ex)
        print("F", end="")

    @staticmethod
    def _test_file_entry(file_name: str):
        print(f"\n{file_name.replace('.cairo', '')}: ", end="")

    async def run_tests_in(self, src: str):
        test_subjects = TestCollector(
            sources_directory=src,
            include_paths=self.include_paths,
        ).collect()
        for test_subject in test_subjects:
            compiled_test = StarknetCompiler(
                include_paths=self.include_paths,
            ).compile_contract(test_subject.test_path)

            TestRunner._test_file_entry(test_subject.test_path.name)
            await self._run_test_functions(
                test_contract=compiled_test,
                functions=test_subject.test_functions,
            )

    async def _run_test_functions(
        self,
        test_contract: ContractDefinition,
        functions: List[dict],
    ):
        starknet = await Starknet.empty()
        contract = await starknet.deploy(contract_def=test_contract)

        for function in functions:
            try:
                func = getattr(contract, function["name"])

                # TODO: Improve stacktrace
                result = await func(contract.contract_address).call()
                self._case_success(result.body)
            except StarkException as ex:
                self._case_failure(ex)
