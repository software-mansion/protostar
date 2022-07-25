from typing import Optional

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    is_fuzz_test,
    FuzzTestExecutionEnvironment,
)
from protostar.commands.test.environments.setup_execution_environment import (
    SetupExecutionEnvironment,
)
from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState


async def invoke_setup(
    function_name: str,
    state: TestExecutionState,
):
    env = SetupExecutionEnvironment(state)
    await env.invoke(function_name)


async def invoke_test_case(
    function_name: str,
    state: TestExecutionState,
) -> Optional[ExecutionResourcesSummary]:
    if is_fuzz_test(function_name, state):
        env = FuzzTestExecutionEnvironment(state)
    else:
        env = TestExecutionEnvironment(state)

    return await env.invoke(function_name)
