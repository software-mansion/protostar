from contextlib import contextmanager
from typing import Optional, Any, Generator

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program


class CairoRunnerFacade:
    def __init__(self, program: Program):
        self._program: Program = program
        self.current_runner: Optional[CairoFunctionRunner] = None
        self._previous_runner: Optional[CairoFunctionRunner] = None

    @contextmanager
    def new_runner(self) -> Generator[CairoFunctionRunner, None, None]:
        self._previous_runner = None
        runner = CairoFunctionRunner(program=self._program, layout="all")
        self.current_runner = runner
        yield runner
        self._previous_runner = runner

    def run_from_offset(
        self,
        offset: int,
        *args: Any,
        hint_locals: Optional[dict] = None,
        **kwargs: Any,
    ):
        with self.new_runner() as function_runner:
            function_runner.run_from_entrypoint(
                *args,
                entrypoint=offset,
                hint_locals=hint_locals or {},
                static_locals={
                    "__find_element_max_size": 2**20,
                    "__squash_dict_max_size": 2**20,
                    "__keccak_max_size": 2**20,
                    "__usort_max_size": 2**20,
                    "__chained_ec_op_max_len": 1000,
                },
                verify_secure=False,
                **kwargs,
            )

    def run_by_function_name(
        self,
        func_name: str,
        *args: Any,
        hint_locals: Optional[dict] = None,
        **kwargs: Any,
    ):
        with self.new_runner() as function_runner:
            function_runner.run(
                func_name, *args, hint_locals=hint_locals or {}, **kwargs
            )

    def get_return_values(self, n_ret: int):
        assert (
            self._previous_runner
        ), "No runs were performed, so no return values are available!"
        return self._previous_runner.get_return_values(n_ret)

    def did_panic(self):
        return self.get_return_values(3)[0] == 1
