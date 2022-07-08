from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Set, Tuple

from starkware.cairo.lang.cairo_constants import DEFAULT_PRIME
from starkware.cairo.lang.compiler.cairo_compile import get_module_reader
from starkware.cairo.lang.compiler.constants import MAIN_SCOPE
from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.cairo.lang.compiler.preprocessor.pass_manager import (
    PassManager,
    PassManagerContext,
    Stage,
)
from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)
from starkware.starknet.compiler.compile import assemble_starknet_contract
from starkware.starknet.compiler.starknet_pass_manager import starknet_pass_manager
from starkware.starknet.compiler.starknet_preprocessor import (
    StarknetPreprocessedProgram,
)
from starkware.starknet.services.api.contract_class import ContractClass

from protostar.protostar_exception import ProtostarException


@dataclass
class StarknetCompiler:
    class FileNotFoundException(ProtostarException):
        pass

    include_paths: List[str]
    disable_hint_validation: bool

    def get_starknet_pass_manager(self) -> PassManager:
        read_module = get_module_reader(cairo_path=self.include_paths).read
        return starknet_pass_manager(
            DEFAULT_PRIME,
            read_module,
            disable_hint_validation=self.disable_hint_validation,
        )

    def get_file_identifiers(self, cairo_file_path: Path) -> List[str]:
        pass_manager = self.get_starknet_pass_manager()
        file_identifiers: Set[str] = set()

        try:
            codes = [(cairo_file_path.read_text("utf-8"), str(cairo_file_path))]
            context = PassManagerContext(
                start_codes=[],
                codes=codes,
                main_scope=MAIN_SCOPE,
                identifiers=IdentifierManager(),
            )

            crucial_stages: List[Tuple[str, Stage]] = [
                stage_pair
                for stage_pair in pass_manager.stages
                if stage_pair[0]
                in [
                    "module_collector",
                    "unique_label_creator",
                    "storage_var_signature",
                    "contract_interface_signature",
                    "event_signature",
                    "identifier_collector",
                ]
            ]
            pass_manager.stages = crucial_stages
            pass_manager.run(context)
            for scoped_name in context.identifiers.dict:
                if "__main__" == scoped_name.path[0]:
                    file_identifiers.add(scoped_name.path[1])
            return list(file_identifiers)
        except FileNotFoundError as err:
            raise StarknetCompiler.FileNotFoundException(
                message=(f"Couldn't find file '{err.filename}'")
            ) from err

    def preprocess_contract(
        self, *cairo_file_paths: Path
    ) -> StarknetPreprocessedProgram:
        pass_manager = self.get_starknet_pass_manager()

        try:
            codes = [
                (cairo_file_path.read_text("utf-8"), str(cairo_file_path))
                for cairo_file_path in cairo_file_paths
            ]
            context = PassManagerContext(
                start_codes=[],
                codes=codes,
                main_scope=MAIN_SCOPE,
                identifiers=IdentifierManager(),
            )

            pass_manager.run(context)
            assert isinstance(context.preprocessed_program, StarknetPreprocessedProgram)
            return context.preprocessed_program
        except FileNotFoundError as err:
            raise StarknetCompiler.FileNotFoundException(
                message=(f"Couldn't find file '{err.filename}'")
            ) from err

    @staticmethod
    def compile_preprocessed_contract(
        preprocessed: StarknetPreprocessedProgram,
        add_debug_info: bool = False,
        is_account_contract: bool = False,
    ) -> ContractClass:
        try:
            assembled = assemble_starknet_contract(
                preprocessed_program=preprocessed,
                main_scope=MAIN_SCOPE,
                add_debug_info=add_debug_info,
                file_contents_for_debug_info={},
                filter_identifiers=False,
                is_account_contract=is_account_contract,
            )
            assert isinstance(assembled, ContractClass)
            return assembled
        except PreprocessorError as err:
            err_message = err.message
            if isinstance(err_message, str) and "account_contract" in err_message:
                raise ProtostarException(
                    err_message.replace("account_contract", "account-contract")
                ) from err
            raise err

    def compile_contract(
        self,
        *sources: Path,
        add_debug_info: bool = False,
        is_account_contract: bool = False,
    ) -> ContractClass:
        preprocessed = self.preprocess_contract(*sources)
        assembled = self.compile_preprocessed_contract(
            preprocessed, add_debug_info, is_account_contract
        )
        return assembled

    @staticmethod
    def get_contract_identifiers(
        preprocessed: StarknetPreprocessedProgram, predicate: Callable[[str], bool]
    ) -> List[str]:
        return [
            el["name"]
            for el in preprocessed.abi
            if el["type"] == "function" and predicate(el["name"])
        ]
