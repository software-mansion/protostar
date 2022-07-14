from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple
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
    PreprocessorStage,
)
from starkware.starknet.security.hints_whitelist import get_hints_whitelist


from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import get_module_reader
from starkware.cairo.lang.compiler.preprocessor.pass_manager import (
    PassManager,
    Stage,
)

from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager


if TYPE_CHECKING:
    from protostar.utils.starknet_compilation import CompilerConfig


class PassManagerFactory(ABC):
    @staticmethod
    @abstractmethod
    def build(config: "CompilerConfig") -> PassManager:
        ...


class StarknetPassManagerFactory(PassManagerFactory):
    @staticmethod
    def build(config: "CompilerConfig") -> PassManager:
        read_module = get_module_reader(cairo_path=config.include_paths).read
        return starknet_pass_manager(
            DEFAULT_PRIME,
            read_module,
            disable_hint_validation=config.disable_hint_validation,
        )


class TestCollectorPassManagerFactory(StarknetPassManagerFactory):
    @staticmethod
    def build(config: "CompilerConfig") -> PassManager:
        pass_manager = super().build(config)
        crucial_stages: List[Tuple[str, Stage]] = [
            stage_pair
            for stage_pair in pass_manager.stages
            if stage_pair[0]
            in [
                "module_collector",
                "unique_label_creator",
                "identifier_collector",
            ]
        ]
        pass_manager.stages = crucial_stages
        return pass_manager


class ProtostarPassMangerFactory(StarknetPassManagerFactory):
    @staticmethod
    def build(config: "CompilerConfig") -> PassManager:
        read_module = get_module_reader(cairo_path=config.include_paths).read
        manager = starknet_pass_manager(
            DEFAULT_PRIME,
            read_module,
            disable_hint_validation=config.disable_hint_validation,
        )
        hint_whitelist = (
            None if config.disable_hint_validation else get_hints_whitelist()
        )
        manager.replace(
            "preprocessor",
            PreprocessorStage(
                DEFAULT_PRIME,
                ProtostarPreprocessor,
                None,
                dict(hint_whitelist=hint_whitelist),
            ),
        )
        return manager


class ProtostarPreprocessor(StarknetPreprocessor):
    """
    This preprocessor includes types used in contracts storage variables in ABI
    """

    def add_abi_storage_var_types(self, elm: CodeElementFunction):
        """
        Adds an entry describing the function to the contract's ABI.
        """
        args = elm.arguments.identifiers
        if elm.returns:
            args.extend(elm.returns.identifiers)
        for arg in args:
            unresolved_arg_type = arg.get_type()
            arg_type = self.resolve_type(unresolved_arg_type)
            abi_type_info = prepare_type_for_abi(arg_type)
            for struct_name in abi_type_info.structs:
                self.add_struct_to_abi(struct_name)

    def visit_CodeElementFunction(self, elm: CodeElementFunction):
        super().visit_CodeElementFunction(elm)
        attr = elm.additional_attributes.get("storage_var")
        if attr is not None:
            self.add_abi_storage_var_types(elm=attr)
            return
