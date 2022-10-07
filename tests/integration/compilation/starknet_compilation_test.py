# pylint: disable=invalid-name
from pathlib import Path

from pytest_mock import MockerFixture

import pytest

from protostar.starknet.compiler.pass_managers import ProtostarPassMangerFactory
from protostar.starknet.compiler.starknet_compilation import (
    CompilerConfig,
    StarknetCompiler,
)


@pytest.fixture(name="compiler")
def compiler_fixture() -> StarknetCompiler:
    return StarknetCompiler(
        config=CompilerConfig(include_paths=[], disable_hint_validation=False),
        pass_manager_factory=ProtostarPassMangerFactory,
    )


async def test_protostar_pass(compiler: StarknetCompiler, mocker: MockerFixture):
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


async def test_preprocessor_exception(compiler: StarknetCompiler):
    with pytest.raises(StarknetCompiler.PreprocessorException):
        compiler.compile_contract(
            Path(__file__).parent / "contract_with_preprocess_error.cairo"
        )
