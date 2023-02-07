from abc import ABC
from typing import Any

from starkware.cairo.lang.compiler.program import Program

from protostar.cairo import HintLocalsDict
from protostar.cairo.cairo_function_executor import CairoFunctionExecutor
from protostar.cairo_testing.cairo_injectable_function_runner import (
    CairoInjectableFunctionRunner,
)
from protostar.cairo_testing.cairo_test_execution_state import CairoTestExecutionState
from protostar.cheatable_starknet.cheatables.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)


class CairoExecutionEnvironment(CairoFunctionExecutor, ABC):
    def __init__(
        self,
        state: CairoTestExecutionState,
        program: Program,
        hint_locals: HintLocalsDict,
    ):
        self.state = state
        self.program = program
        self.hint_locals = hint_locals

    async def run_cairo_function(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        CheatableSysCallHandler.block_info_controller_state = (
            self.state.block_info_controller_state
        )
        CheatableSysCallHandler.contracts_controller_state = (
            self.state.contracts_controller_state
        )
        await CairoInjectableFunctionRunner(
            hint_locals=self.hint_locals, program=self.program
        ).run_cairo_function(function_name, *args, **kwargs)
