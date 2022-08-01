import sys

from starkware.cairo.lang.vm.vm_core import VirtualMachine
from starkware.cairo.lang.vm.vm_exceptions import HintException

from hypothesis.errors import UnsatisfiedAssumption

from protostar.commands.test.fuzzing.exceptions import HypothesisRejectException
from protostar.starknet.delayed_builder import DelayedBuilder


class CheatableVirtualMachine(VirtualMachine):
    """
    `VirtualMachine` with modified `step` function that builds cheatcodes created with `DelayedBuilder`.
    It also modifies the `exec_hint` function in order to smuggle `hypothesis` exceptions through te CairoVM.
    """

    # pylint: disable=C0103,W0212
    def step(self):
        self.skip_instruction_execution = False
        # Execute hints.
        for hint_index, hint in enumerate(self.hints.get(self.run_context.pc, [])):
            exec_locals = self.exec_scopes[-1]
            exec_locals["memory"] = memory = self.validated_memory
            exec_locals["ap"] = ap = self.run_context.ap
            exec_locals["fp"] = fp = self.run_context.fp
            exec_locals["pc"] = pc = self.run_context.pc
            exec_locals["current_step"] = self.current_step
            exec_locals["ids"] = hint.consts(pc, ap, fp, memory)

            exec_locals["vm_load_program"] = self.load_program
            exec_locals["vm_enter_scope"] = self.enter_scope
            exec_locals["vm_exit_scope"] = self.exit_scope
            exec_locals.update(self.static_locals)
            exec_locals.update(self.builtin_runners)

            # --- MODIFICATIONS START ---
            for name, value in exec_locals.items():
                if isinstance(value, DelayedBuilder):
                    exec_locals[name] = value.internal_build(exec_locals)
            # --- MODIFICATIONS END ---

            self.exec_hint(hint.compiled, exec_locals, hint_index=hint_index)

            # There are memory leaks in 'exec_scopes'.
            # So, we clear some fields in order to reduce the problem.
            for name in self.builtin_runners:
                del exec_locals[name]

            for name in self.static_locals:
                del exec_locals[name]

            del exec_locals["vm_exit_scope"]
            del exec_locals["vm_enter_scope"]
            del exec_locals["vm_load_program"]
            del exec_locals["ids"]
            del exec_locals["memory"]

            if self.skip_instruction_execution:
                return

        # Decode.
        instruction = self.decode_current_instruction()

        # Run.
        self.run_instruction(instruction)

    # pylint: disable=exec-used
    def exec_hint(self, code, globals_, hint_index):
        """
        Executes the given code with the given globals.
        This function can be overridden by subclasses.
        """
        try:
            exec(code, globals_)
        # --- MODIFICATIONS START ---
        except UnsatisfiedAssumption as exc:
            raise HypothesisRejectException(exc) from exc
        # --- MODIFICATIONS END ---
        except Exception:
            hint_exception = HintException(self, *sys.exc_info())
            raise self.as_vm_exception(
                hint_exception,
                notes=[hint_exception.exception_str],
                hint_index=hint_index,
            ) from None
