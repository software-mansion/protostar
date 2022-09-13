from typing import Optional, Dict, Any
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from protostar.starknet.cheatable_cairo_vm import CheatableVirtualMachine


class CheatableCairoFunctionRunner(CairoFunctionRunner):
    """
    CairoFunctionRunner which uses CheatableVirtualMachine instead of a regular VirtualMachine
    """

    def initialize_vm(  # type: ignore
        self,
        hint_locals,
        static_locals: Optional[Dict[str, Any]] = None,
        vm_class=CheatableVirtualMachine,
    ):
        super().initialize_vm(hint_locals, static_locals, vm_class)
