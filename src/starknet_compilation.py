from pathlib import Path

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


def get_starknet_pass_manager() -> PassManager:
    read_module = get_module_reader(
        cairo_path=[]  # TODO: Include installed project libs here, for compilation
    ).read
    return starknet_pass_manager(DEFAULT_PRIME, read_module)


def preprocess_contract(cairo_file_path: Path) -> StarknetPreprocessedProgram:
    pass_manager = get_starknet_pass_manager()

    codes = [(cairo_file_path.read_text("utf-8"), str(cairo_file_path))]
    context = PassManagerContext(
        codes=codes,
        main_scope=MAIN_SCOPE,
        identifiers=IdentifierManager(),
    )
    pass_manager.run(context)
    assert isinstance(context.preprocessed_program, StarknetPreprocessedProgram)
    return context.preprocessed_program


def compile_contract(cairo_file_path: Path) -> ContractDefinition:
    preprocessed = preprocess_contract(cairo_file_path)
    assembled = assemble_starknet_contract(
        preprocessed_program=preprocessed,
        main_scope=MAIN_SCOPE,
        add_debug_info=False,
        file_contents_for_debug_info={},
    )
    assert isinstance(assembled, ContractDefinition)
    return assembled
