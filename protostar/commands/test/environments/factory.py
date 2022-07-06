from typing import Optional

from protostar.commands.test.environments.setup_execution_environment import (
    SetupExecutionEnvironment,
)
from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.commands.test.execution_state import ExecutionState
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)


async def invoke_setup(function_name: str, state: ExecutionState):
    env = SetupExecutionEnvironment(state)
    await env.invoke(function_name)


async def invoke_test_case(
    function_name: str, state: ExecutionState
) -> Optional[ExecutionResourcesSummary]:
    env = TestExecutionEnvironment(state)
    return await env.invoke(function_name)
