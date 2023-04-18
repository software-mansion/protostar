import asyncio
from contextlib import contextmanager
from typing import Any

from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.vm_exceptions import VmException

from protostar.cairo import HintLocalsDict
from protostar.cairo.cairo_function_executor import Offset, OffsetOrName
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade
from protostar.cairo.short_string import short_string_to_str
from protostar.testing.test_environment_exceptions import RevertableException
from protostar.starknet import SimpleReportedException


class CairoInjectableFunctionRunner:
    def __init__(self, hint_locals: HintLocalsDict, program: Program):
        self._hint_locals = hint_locals
        self._cairo_runner_facade = CairoRunnerFacade(program=program)

    async def run_cairo_function(
        self,
        function_identifier: OffsetOrName,
        *args: Any,
        **kwargs: Any,
    ):
        loop = asyncio.get_running_loop()

        def function_runner():
            if isinstance(function_identifier, Offset):
                self.run_cairo_function_by_offset(function_identifier, *args, **kwargs)
            else:
                self.run_cairo_function_by_name(function_identifier, *args, **kwargs)

        await loop.run_in_executor(
            executor=None,
            func=function_runner,
        )

    def run_cairo_function_by_offset(
        self,
        offset: Offset,
        *args: Any,
        **kwargs: Any,
    ):
        with self.vm_exception_handling():
            self._cairo_runner_facade.run_from_offset(
                offset=offset, hint_locals=self._hint_locals, *args, **kwargs
            )
            if self._cairo_runner_facade.did_panic():
                panic_data = self._cairo_runner_facade.get_panic_data()
                panic_data_short_strs = [
                    short_string_to_str(datum) for datum in panic_data
                ]
                raise SimpleReportedException(
                    f"Test failed with data: \n"
                    f"{panic_data} (integer representation)\n"
                    f"{panic_data_short_strs} (short-string representation)"
                )

    def run_cairo_function_by_name(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        with self.vm_exception_handling():
            self._cairo_runner_facade.run_by_function_name(
                function_name,
                hint_locals=self._hint_locals,
                *args,
                **kwargs,
            )

    @contextmanager
    def vm_exception_handling(self):
        try:
            yield
        except VmException as vm_ex:
            error_message = vm_ex.message
            if hasattr(vm_ex.inner_exc, "exception_str"):
                error_message += vm_ex.inner_exc.exception_str

            raise RevertableException(error_message) from vm_ex
