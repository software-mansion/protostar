# pylint: disable=invalid-name
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


from protostar.commands.test.starkware.forkable_starknet import ForkableStarknet
from protostar.commands.test.test_execution_environment import TestExecutionEnvironment
from protostar.utils.starknet_compilation import StarknetCompiler

@pytest.fixture(name="compiled_contract")
def contract():
    compiled_contract = StarknetCompiler(
        disable_hint_validation=True,
        include_paths=[]
    ).compile_contract(
        Path(__file__).parent / "global_storage.cairo", add_debug_info=True
    )
    return compiled_contract



@pytest.fixture(name="test_environment")
@pytest.mark.asyncio
async def test_exec_env(compiled_contract):
    return await TestExecutionEnvironment.empty(
                compiled_contract, []
            )



@pytest.mark.asyncio
async def test_environment_preserves_global_storage(test_environment):
    await test_environment.invoke_test_case("before")
    await test_environment.invoke_test_case("after")


@pytest.mark.asyncio
async def test_forkable_starknet_preserves_global_storage_when_forked(test_environment):
    await test_environment.invoke_test_case("before")
    test_environment = test_environment.fork()
    await test_environment.invoke_test_case("after")

