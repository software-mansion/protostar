from pathlib import Path

from starkware.starknet.public.abi import AbiType

from protostar.starknet.pass_managers import (
    StarknetPassManagerFactory,
    TestSuitePassMangerFactory,
)
from protostar.starknet import StarknetCompilerConfig, StarknetCompiler


def oracle_abi() -> AbiType:
    original_compiler = StarknetCompiler(
        config=StarknetCompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=StarknetPassManagerFactory,
    )
    abi = original_compiler.compile_contract(
        Path(__file__).parent / "test_unit_with_constructor.cairo"
    ).abi
    assert abi
    return abi


async def test_case_compile_pass_removes_constructor_oracle():
    compiler = StarknetCompiler(
        config=StarknetCompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestSuitePassMangerFactory,
    )
    contract_class = compiler.compile_contract(
        Path(__file__).parent / "test_unit_with_constructor.cairo"
    )
    assert contract_class.abi
    assert not [el for el in contract_class.abi if el["type"] == "constructor"]
    assert [
        el for el in oracle_abi() if el["type"] != "constructor"
    ] == contract_class.abi


async def test_case_compile_pass_removes_namespace_constructor_oracle():
    compiler = StarknetCompiler(
        config=StarknetCompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestSuitePassMangerFactory,
    )
    contract_class = compiler.compile_contract(
        Path(__file__).parent / "test_unit_with_namespace_constructor.cairo"
    )
    assert contract_class.abi
    assert not [el for el in contract_class.abi if el["type"] == "constructor"]
    assert [
        el for el in oracle_abi() if el["type"] != "constructor"
    ] == contract_class.abi
