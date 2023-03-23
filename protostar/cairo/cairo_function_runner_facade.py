from contextlib import contextmanager
from typing import Optional, Any, Generator, Union

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.utils import RunResources
from starkware.cairo.lang.vm.relocatable import MaybeRelocatable
from starkware.cairo.lang.vm.security import verify_secure_runner


RUNNER_BUILTINS = ["pedersen", "range_check", "bitwise", "ec_op"]
RUNNER_BUILTINS_CAMEL_CASE = [
    "".join(x.title() for x in builtin.split("_")[:]) for builtin in RUNNER_BUILTINS
]


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
            self.run_as_main(
                function_runner,
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

    # pylint: disable=unused-argument
    @staticmethod
    def run_as_main(
        function_runner: CairoFunctionRunner,
        entrypoint: Union[str, int],
        *args,  # type: ignore
        typed_args: Optional[bool] = False,
        hint_locals: Optional[dict[str, Any]] = None,
        static_locals: Optional[dict[str, Any]] = None,
        run_resources: Optional[RunResources] = None,
        verify_secure: Optional[bool] = None,
        apply_modulo_to_args: Optional[bool] = None,
    ):
        """
        Runs the program from the given entrypoint.

        Additional params:
        typed_args - If true, the arguments are given as Cairo typed NamedTuple generated
          with CairoStructFactory.
        verify_secure - Run verify_secure_runner to do extra verifications.
        apply_modulo_to_args - Apply modulo operation on integer arguments.
        """
        if hint_locals is None:
            hint_locals = {}

        if verify_secure is None:
            verify_secure = True

        if apply_modulo_to_args is None:
            apply_modulo_to_args = True

        stack: list[MaybeRelocatable] = []
        for builtin_name in function_runner.program.builtins:
            builtin_runner = function_runner.builtin_runners.get(
                f"{builtin_name}_builtin"
            )
            if builtin_runner is None:
                assert function_runner.allow_missing_builtins, "Missing builtin."
                stack += [0]
            else:
                stack += builtin_runner.initial_stack()
        end = function_runner.initialize_function_entrypoint(
            entrypoint=entrypoint, args=stack
        )

        function_runner.initialize_vm(
            hint_locals=hint_locals, static_locals=static_locals
        )

        function_runner.run_until_pc(addr=end, run_resources=run_resources)
        function_runner.end_run()

        if verify_secure:
            verify_secure_runner(runner=function_runner, verify_builtins=False)

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

    def did_panic(self) -> bool:
        return bool(self.get_panic_data())

    def get_panic_data(self) -> list[int]:
        assert self._previous_runner
        result = self.get_return_values(3)

        if result[0] == 0:
            return []

        panic_data_start = result[1]
        panic_data_end = result[2]
        iterator = panic_data_start
        panic_data = []
        while iterator != panic_data_end:
            panic_data.append(self._previous_runner.vm_memory.data[iterator])
            iterator = iterator + 1
        return panic_data
