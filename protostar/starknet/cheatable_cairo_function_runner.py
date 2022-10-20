from typing import Optional, Dict, Any, Type
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.vm_core import VirtualMachine

from protostar.starknet.cheatable_cairo_vm import CheatableVirtualMachine


class CheatableCairoFunctionRunner(CairoFunctionRunner):
    """
    CairoFunctionRunner which uses CheatableVirtualMachine instead of a regular VirtualMachine
    """

    def initialize_vm(
        self,
        hint_locals: Dict[str, Any],
        static_locals: Optional[Dict[str, Any]] = None,
        vm_class: Type[VirtualMachine] = CheatableVirtualMachine,
    ):
        super().initialize_vm(hint_locals, static_locals, vm_class)
