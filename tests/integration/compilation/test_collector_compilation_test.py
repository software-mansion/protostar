from pathlib import Path

from pytest_mock import MockerFixture

from protostar.utils.compiler.pass_managers import (
    ProtostarPassMangerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


def expected_collected_functions_oracle(path: Path):
    default_compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=ProtostarPassMangerFactory,
    )
    contract_class = default_compiler.preprocess_contract(path)
    return [el["name"] for el in contract_class.abi if el["type"] == "function"]


async def test_test_collector_pass_oracle(mocker: MockerFixture):
    compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestCollectorPassManagerFactory,
    )
    file_path = Path(__file__).parent / "collector_contract.cairo"
    
    contract_class = compiler.preprocess_contract(file_path)

    assert contract_class.abi
    assert set([el["name"] for el in contract_class.abi]) == set(expected_collected_functions_oracle(file_path))
    assert all([el["type"] == "function" for el in contract_class.abi])