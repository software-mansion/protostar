import asyncio
from typing import Any

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.vm_exceptions import VmException

from protostar.cairo import HintLocalsDict
from protostar.testing.test_environment_exceptions import RevertableException


class CairoInjectableFunctionRunner:
    def __init__(self, hint_locals: HintLocalsDict, program: Program):
        self._hint_locals = hint_locals
        self._program = program

    async def run_cairo_function(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            executor=None,
            func=lambda: self.run_cairo_function_sync(function_name, *args, **kwargs),
        )

    def run_cairo_function_sync(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        try:
            runner = CairoFunctionRunner(program=self._program, layout="starknet")
            runner.run(function_name, *args, hint_locals=self._hint_locals, **kwargs)
        except VmException as vm_ex:
            error_message = vm_ex.message
            if hasattr(vm_ex.inner_exc, "exception_str"):
                error_message += vm_ex.inner_exc.exception_str

            raise RevertableException(error_message) from vm_ex
