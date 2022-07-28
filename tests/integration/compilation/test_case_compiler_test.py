from pathlib import Path

from pytest_mock import MockerFixture

from protostar.utils.compiler.pass_managers import (
    StarknetPassManagerFactory,
    TestCasePassMangerFactory,
)
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler

def oracle_abi():
    original_compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=StarknetPassManagerFactory,
    )
    return original_compiler.compile_contract(Path(__file__).parent / "test_unit_with_constructor.cairo").abi


async def test_case_compile_pass_removes_constructor_oracle(mocker: MockerFixture):
    compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestCasePassMangerFactory,
    )
    contract_class = compiler.compile_contract(Path(__file__).parent / "test_unit_with_constructor.cairo")
    assert contract_class.abi
    assert not [el for el in contract_class.abi if el["type"] == "constructor"]
    assert [el for el in oracle_abi() if el["type"] != "constructor"] == contract_class.abi


async def test_case_compile_pass_removes_namespace_constructor_oracle(mocker: MockerFixture):
    compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestCasePassMangerFactory,
    )
    contract_class = compiler.compile_contract(Path(__file__).parent / "test_unit_with_namespace_constructor.cairo")
    assert contract_class.abi
    assert not [el for el in contract_class.abi if el["type"] == "constructor"]
    assert [el for el in oracle_abi() if el["type"] != "constructor"] == contract_class.abi
