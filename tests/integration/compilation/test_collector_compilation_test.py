from pathlib import Path

from protostar.utils.compiler.pass_managers import (
    ProtostarPassMangerFactory,
    TestCollectorPassManagerFactory,
)
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


def preview(abi_entry: dict) -> tuple:
    """
    Returns a preview object of ABI entry that is hashable, so it can be added to a set.
    """
    return abi_entry["name"], abi_entry["type"]


def expected_collected_functions_oracle(path: Path):
    default_compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=ProtostarPassMangerFactory,
    )
    contract_class = default_compiler.preprocess_contract(path)
    return [preview(el) for el in contract_class.abi if el["type"] == "function"]


async def test_test_collector_pass_oracle():
    compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestCollectorPassManagerFactory,
    )
    file_path = Path(__file__).parent / "collector_contract.cairo"

    contract_class = compiler.preprocess_contract(file_path)

    assert contract_class.abi
    assert set(preview(el) for el in contract_class.abi) == set(
        expected_collected_functions_oracle(file_path)
    )
