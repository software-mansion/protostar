
from starkware.starknet.public.abi_structs import (
    prepare_type_for_abi,
)
from starkware.cairo.lang.compiler.ast.code_elements import (
    CodeElementFunction,
)
from starkware.starknet.compiler.starknet_preprocessor import StarknetPreprocessor

from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import get_module_reader
from starkware.cairo.lang.compiler.preprocessor.pass_manager import (
    PassManager,
)
from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager


from starkware.cairo.lang.compiler.preprocessor.default_pass_manager import (
    PreprocessorStage
)

def get_protostar_pass_manager(include_paths, disable_hint_validation) -> PassManager:
    read_module = get_module_reader(cairo_path=include_paths).read
    manager = starknet_pass_manager(
        DEFAULT_PRIME,
        read_module,
        disable_hint_validation=disable_hint_validation,
    )
    manager.replace(
        "preprocessor",
        PreprocessorStage(DEFAULT_PRIME, ProtostarPreprocessor, None, None),
    )
    return manager

class ProtostarPreprocessor(StarknetPreprocessor):
    """
    Preprocessor which includes more information in ABI
    """

    def add_abi_storage_var_types(self, elm: CodeElementFunction):
        """
        Adds an entry describing the function to the contract's ABI.
        """
        for arg in elm.arguments.identifiers + elm.returns.identifiers:
            unresolved_arg_type = arg.get_type()
            arg_type = self.resolve_type(unresolved_arg_type)
            abi_type_info = prepare_type_for_abi(arg_type)
            for struct_name in abi_type_info.structs:
                self.add_struct_to_abi(struct_name)

    def visit_CodeElementFunction(self, elm: CodeElementFunction):
        super().visit_CodeElementFunction(elm)
        attr = elm.additional_attributes.get("storage_var")
        if attr is not None:
            self.add_abi_storage_var_types(
                elm=attr
            )
            return