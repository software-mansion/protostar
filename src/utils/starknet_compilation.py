from dataclasses import dataclass
from pathlib import Path
from typing import List

from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import (
    get_module_reader,
)
from starkware.cairo.lang.compiler.constants import MAIN_SCOPE
from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.cairo.lang.compiler.preprocessor.pass_manager import (
    PassManagerContext,
    PassManager,
)
from starkware.starknet.compiler.compile import assemble_starknet_contract
from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager
from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)
from starkware.starknet.services.api.contract_definition import ContractDefinition


@dataclass
class StarknetCompiler:
    include_paths: List[str]

    def get_starknet_pass_manager(self) -> PassManager:
        read_module = get_module_reader(cairo_path=self.include_paths).read
        return starknet_pass_manager(DEFAULT_PRIME, read_module)

    def preprocess_contract(
        self, *cairo_file_paths: Path
    ) -> StarknetPreprocessedProgram:
        pass_manager = self.get_starknet_pass_manager()

        codes = [
            (cairo_file_path.read_text("utf-8"), str(cairo_file_path))
            for cairo_file_path in cairo_file_paths
        ]
        context = PassManagerContext(
            codes=codes,
            main_scope=MAIN_SCOPE,
            identifiers=IdentifierManager(),
        )
        pass_manager.run(context)
        assert isinstance(context.preprocessed_program, StarknetPreprocessedProgram)
        return context.preprocessed_program

    def compile_contract(self, *sources: Path) -> ContractDefinition:
        preprocessed = self.preprocess_contract(*sources)
        assembled = assemble_starknet_contract(
            preprocessed_program=preprocessed,
            main_scope=MAIN_SCOPE,
            add_debug_info=False,
            file_contents_for_debug_info={},
        )
        assert isinstance(assembled, ContractDefinition)
        return assembled
