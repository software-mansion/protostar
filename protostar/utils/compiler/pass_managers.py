from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
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
    PassManagerContext,
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
    VisitorStage,
)
from starkware.cairo.lang.compiler.preprocessor.default_pass_manager import (
    ModuleCollector,
)
from starkware.starknet.compiler.external_wrapper import (
    parse_entry_point_decorators,
)
from starkware.starknet.public.abi import AbiType

from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager
from starkware.cairo.lang.compiler.ast.code_elements import (
    CodeElementFunction,
)
from starkware.cairo.lang.compiler.ast.visitor import Visitor
from starkware.starknet.compiler.external_wrapper import get_abi_entry_type

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
        read_module = get_module_reader(cairo_path=config.include_paths).read

        manager = PassManager()
        manager.add_stage(
            "module_collector",
            ModuleCollector(
                read_module=read_module,
                additional_modules=[],
            ),
        )
        collector_fac: Callable[
            [PassManagerContext], Visitor
        ] = lambda _: TestCollectorPreprocessor()
        manager.add_stage(
            "test_collector_preprocessor",
            new_stage=TestCollectorStage(
                collector_fac,
                modify_ast=True,
            ),
        )
        return manager


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


class TestCollectorStage(VisitorStage):
    def run(self, context: PassManagerContext):
        visitor = self.visitor_factory(context)
        modified_modules = []
        for module in context.modules:
            modified_modules.append(visitor.visit(module))
        if self.modify_ast:
            context.modules = modified_modules
        context.preprocessed_program = visitor.get_program()
        return visitor


@dataclass
class TestCollectorPreprocessedProgram:
    abi: AbiType


class TestCollectorPreprocessor(Visitor):
    def __init__(self):
        super().__init__()
        self.abi: AbiType = []

    """
    This preprocessor generates simpler and more limited ABI in exchange for performance.
    ABI includes only function types with only names.
    """

    def add_simple_abi_function_entry(
        self, elm: CodeElementFunction, external_decorator_name: str
    ):
        """
        Adds an entry describing the function to the contract's ABI.
        """
        entry_type = get_abi_entry_type(external_decorator_name=external_decorator_name)
        self.abi.append(
            {
                "name": elm.name,
                "type": entry_type,
            }
        )

    def visit_CodeElementFunction(self, elm: CodeElementFunction):
        external_decorator, _, _ = parse_entry_point_decorators(elm=elm)
        if external_decorator is not None:

            # Add a function/constructor entry to the ABI.
            self.add_simple_abi_function_entry(
                elm=elm,
                external_decorator_name=external_decorator.name,
            )

    def get_program(self):
        return TestCollectorPreprocessedProgram(abi=self.abi)

    def _visit_default(self, obj):
        pass
