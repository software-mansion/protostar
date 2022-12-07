from starkware.cairo.lang.vm.vm_core import VirtualMachine

from protostar.starknet.delayed_builder import DelayedBuilder


class CheatableVirtualMachine(VirtualMachine):
    """
    `VirtualMachine` with modified `step` function that builds cheatcodes created with `DelayedBuilder`.
    """

    def exec_hint(
        self, code, globals_, hint_index
    ):  # pyright: reportMissingParameterType=false
        for name, value in globals_.items():
            if isinstance(value, DelayedBuilder):
                globals_[name] = value.internal_build(globals_)

        return super().exec_hint(code, globals_, hint_index)
