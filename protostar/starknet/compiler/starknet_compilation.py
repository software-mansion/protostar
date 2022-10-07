from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Type, Union

from starkware.cairo.lang.compiler.constants import MAIN_SCOPE
from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.cairo.lang.compiler.preprocessor.pass_manager import (
    PassManagerContext,
)
from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.starknet.compiler.compile import assemble_starknet_contract
from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)
from starkware.starknet.services.api.contract_class import ContractClass

from protostar.protostar_exception import ProtostarException
from protostar.starknet.compiler.pass_managers import (
    PassManagerFactory,
    TestCollectorPreprocessedProgram,
)


@dataclass(frozen=True)
class CompilerConfig:
    include_paths: List[str]
    disable_hint_validation: bool


class StarknetCompiler:
    def __init__(
        self,
        config: CompilerConfig,
        pass_manager_factory: Type[PassManagerFactory],
    ):
        self.pass_manager = pass_manager_factory.build(config)

    class FileNotFoundException(ProtostarException):
        pass

    @staticmethod
    def build_context(codes: List[Tuple[str, str]]) -> PassManagerContext:
        return PassManagerContext(
            start_codes=[],
            codes=codes,
            main_scope=MAIN_SCOPE,
            identifiers=IdentifierManager(),
        )

    @staticmethod
    def build_codes(*cairo_file_paths: Path) -> List[Tuple[str, str]]:
        return [
            (cairo_file_path.read_text("utf-8"), str(cairo_file_path))
            for cairo_file_path in cairo_file_paths
        ]

    def preprocess_contract(
        self, *cairo_file_paths: Path
    ) -> Union[StarknetPreprocessedProgram, TestCollectorPreprocessedProgram]:
        try:
            codes = self.build_codes(*cairo_file_paths)
            context = self.build_context(codes)
            self.pass_manager.run(context)
            assert isinstance(
                context.preprocessed_program,
                (StarknetPreprocessedProgram, TestCollectorPreprocessedProgram),
            )
            return context.preprocessed_program
        except FileNotFoundError as err:
            raise StarknetCompiler.FileNotFoundException(
                message=(f"Couldn't find file '{err.filename}'")
            ) from err

    @staticmethod
    def compile_preprocessed_contract(
        preprocessed: StarknetPreprocessedProgram,
        add_debug_info: bool = False,
    ) -> ContractClass:
        try:
            return assemble_starknet_contract(
                preprocessed_program=preprocessed,
                main_scope=MAIN_SCOPE,
                add_debug_info=add_debug_info,
                file_contents_for_debug_info={},
                filter_identifiers=False,
                is_account_contract=False,
            )
        except PreprocessorError as err:
            if isinstance(err.message, str) and "account_contract" in err.message:
                return assemble_starknet_contract(
                    preprocessed_program=preprocessed,
                    main_scope=MAIN_SCOPE,
                    add_debug_info=add_debug_info,
                    file_contents_for_debug_info={},
                    filter_identifiers=False,
                    is_account_contract=True,
                )
            raise err

    def compile_contract(
        self,
        *sources: Path,
        add_debug_info: bool = False,
    ) -> ContractClass:
        preprocessed = self.preprocess_contract(*sources)
        assert isinstance(preprocessed, StarknetPreprocessedProgram)
        assembled = self.compile_preprocessed_contract(preprocessed, add_debug_info)
        return assembled

    @staticmethod
    def get_function_names(
        preprocessed: Union[
            StarknetPreprocessedProgram, TestCollectorPreprocessedProgram
        ],
    ) -> List[str]:
        return [el["name"] for el in preprocessed.abi if el["type"] == "function"]
