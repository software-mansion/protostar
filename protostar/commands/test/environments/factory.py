from io import StringIO
from typing import Optional
from contextlib import redirect_stdout

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
from protostar.commands.test.test_output_recorder import OutputName


async def invoke_setup(
    function_name: str,
    state: TestExecutionState,
    output_name: OutputName,
) -> Optional[ExecutionResourcesSummary]:
    env = TestExecutionEnvironment(state)
    return await env.invoke(function_name, output_name)


async def invoke_test_case(
    function_name: str,
    state: TestExecutionState,
    output_name: OutputName,
) -> Optional[ExecutionResourcesSummary]:
    env = TestExecutionEnvironment(state)
    return await env.invoke(function_name, output_name)
