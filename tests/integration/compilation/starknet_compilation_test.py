# pylint: disable=invalid-name
from pathlib import Path

from pytest_mock import MockerFixture

from protostar.utils.compiler.pass_managers import ProtostarPassMangerFactory, TestCollectorPassManagerFactory
from protostar.utils.starknet_compilation import CompilerConfig, StarknetCompiler


async def test_protostar_pass(mocker: MockerFixture):
    compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=ProtostarPassMangerFactory,
    )

    contract_class = compiler.compile_contract(Path(__file__).parent / "contract.cairo")

    first_type = {
        "name": "Key",
        "type": "struct",
        "members": [
            {"name": "a", "type": "felt", "offset": 0},
            {"name": "b", "type": "felt", "offset": 1},
        ],
        "size": 2,
    }
    second_type = {
        "name": "Value",
        "type": "struct",
        "members": [
            {"name": "a", "type": "felt", "offset": 0},
            {"name": "b", "type": "felt", "offset": 1},
        ],
        "size": 2,
    }
    assert contract_class.abi
    assert first_type in contract_class.abi
    assert second_type in contract_class.abi


async def test_test_collector_pass(mocker: MockerFixture):
    compiler = StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=TestCollectorPassManagerFactory,
    )

    contract_class = compiler.preprocess_contract(Path(__file__).parent / "collector_contract.cairo")

    first_type = {
        "name": "test_case1",
        "type": "function"
    }
    second_type = {
        "name": "test_case2",
        "type": "function"
    }

    assert contract_class.abi
    assert first_type in contract_class.abi
    assert second_type in contract_class.abi