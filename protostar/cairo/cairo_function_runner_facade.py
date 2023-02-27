from typing import Optional, Any

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program


class CairoRunnerFacade:
    def __init__(self, program: Program):
        self._program = program
        self._runner = CairoFunctionRunner(program=program, layout="all")

    def run_from_offset(
        self,
        offset: int,
        *args: Any,
        hint_locals: Optional[dict] = None,
        **kwargs: Any,
    ):
        self._runner.run_from_entrypoint(
            offset,
            *args,
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
        self._runner.run(func_name, *args, hint_locals=hint_locals or {}, **kwargs)

    def get_return_values(self, n_ret: int):
        return self._runner.get_return_values(n_ret)
