from pathlib import Path
from typing import Optional, Tuple
import protostar.cairo.cairo_bindings as cairo1_bindings
from protostar.protostar_exception import ProtostarException


class SierraCompilationException(ProtostarException):
    def __init__(self, contract_name: str, err: Exception):
        super().__init__(
            f"Failed to compile contract {contract_name} to sierra\n{str(err)}"
        )


class CasmCompilationException(ProtostarException):
    def __init__(self, contract_name: str, err: Exception):
        super().__init__(
            f"Failed to compile contract {contract_name} to casm\n{str(err)}"
        )


class Cairo1ContractCompiler:
    @staticmethod
    def compile_contract(
        contract_name: str,
        contract_path: Path,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> Tuple[str, str]:
        sierra_compiled = Cairo1ContractCompiler.compile_contract_to_sierra(
            contract_name, contract_path, cairo_path, output_path
        )
        casm_compiled = Cairo1ContractCompiler.compile_contract_to_casm(
            contract_name, contract_path, cairo_path, output_path
        )
        return sierra_compiled, casm_compiled

    @staticmethod
    def compile_contract_to_sierra(
        contract_name: str,
        contract_path: Path,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        if output_path:
            output_path = output_path.with_suffix(".sierra.json")

        try:
            sierra_compiled = (
                cairo1_bindings.compile_starknet_contract_to_sierra_from_path(
                    input_path=contract_path,
                    cairo_path=cairo_path,
                    output_path=output_path,
                )
            )

        except cairo1_bindings.CairoBindingException as ex:
            raise SierraCompilationException(
                contract_name=contract_name, err=ex
            ) from ex

        assert sierra_compiled is not None
        return sierra_compiled

    @staticmethod
    def compile_contract_to_casm(
        contract_name: str,
        contract_path: Path,
        cairo_path: Optional[list[Path]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        if output_path:
            output_path = output_path.with_suffix(".casm.json")

        try:
            casm_compiled = cairo1_bindings.compile_starknet_contract_to_casm_from_path(
                input_path=contract_path, cairo_path=cairo_path, output_path=output_path
            )

        except cairo1_bindings.CairoBindingException as ex:
            raise CasmCompilationException(contract_name=contract_name, err=ex) from ex

        assert casm_compiled is not None
        return casm_compiled
