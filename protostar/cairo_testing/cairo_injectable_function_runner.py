import asyncio
from contextlib import contextmanager
from typing import Any

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.vm_exceptions import VmException

from protostar.cairo import HintLocalsDict
from protostar.cairo.cairo_function_executor import Offset, OffsetOrName
from protostar.testing.test_environment_exceptions import RevertableException


class CairoInjectableFunctionRunner:
    def __init__(self, hint_locals: HintLocalsDict, program: Program):
        self._hint_locals = hint_locals
        self._program = program

    async def run_cairo_function(
        self,
        function_identifier: OffsetOrName,
        *args: Any,
        **kwargs: Any,
    ):
        loop = asyncio.get_running_loop()

        if isinstance(function_identifier, Offset):
            executor = lambda: self.run_cairo_function_by_offset(
                function_identifier, *args, **kwargs
            )
        else:
            executor = lambda: self.run_cairo_function_by_name(
                function_identifier, *args, **kwargs
            )

        await loop.run_in_executor(
            executor=None,
            func=executor,
        )

    def run_cairo_function_by_offset(
        self,
        offset: Offset,
        *args: Any,
        **kwargs: Any,
    ):
        with self.vm_exception_handling():
            pass  # TODO: Implement

    def run_cairo_function_by_name(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        with self.vm_exception_handling():
            runner = CairoFunctionRunner(program=self._program, layout="all")
            runner.run(function_name, *args, hint_locals=self._hint_locals, **kwargs)

    @contextmanager
    def vm_exception_handling(self):
        try:
            yield
        except VmException as vm_ex:
            error_message = vm_ex.message
            if hasattr(vm_ex.inner_exc, "exception_str"):
                error_message += vm_ex.inner_exc.exception_str

            raise RevertableException(error_message) from vm_ex
