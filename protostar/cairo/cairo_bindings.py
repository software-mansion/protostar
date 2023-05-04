import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

import cairo_python_bindings
from protostar.cairo.cairo_function_runner_facade import RUNNER_BUILTINS_TITLE_CASE


class CairoBindingException(Exception):
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


def ensure_output_path(output_path: Optional[Path]):
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)


AvailableGas = Optional[int]


@dataclass
class TestCollectorOutput:
    sierra_output: Optional[str]
    collected_tests: list[tuple[str, AvailableGas]]


def compile_starknet_contract_to_casm_from_path(
    input_path: Path,
    output_path: Optional[Path] = None,
    cairo_path: Optional[list[Path]] = None,
) -> Optional[str]:
    ensure_output_path(output_path=output_path)
    with handle_bindings_errors("compile_starknet_contract_to_casm_from_path"):
        return cairo_python_bindings.compile_starknet_contract_to_casm_from_path(  # pyright: ignore
            str(input_path),
            str(output_path) if output_path else None,
            [str(path) for path in cairo_path] if cairo_path else None,
        )


def compile_starknet_contract_to_sierra_from_path(
    input_path: Path,
    output_path: Optional[Path] = None,
    cairo_path: Optional[list[Path]] = None,
) -> Optional[str]:
    ensure_output_path(output_path=output_path)
    with handle_bindings_errors("compile_starknet_contract_to_sierra_from_path"):
        return cairo_python_bindings.compile_starknet_contract_to_sierra_from_path(  # pyright: ignore
            str(input_path),
            str(output_path) if output_path else None,
            [str(path) for path in cairo_path] if cairo_path else None,
        )


def compile_starknet_contract_sierra_to_casm_from_path(
    input_path: Path,
    output_path: Optional[Path] = None,
) -> Optional[str]:
    ensure_output_path(output_path=output_path)
    with handle_bindings_errors("compile_starknet_contract_to_sierra_from_path"):
        return cairo_python_bindings.compile_starknet_contract_sierra_to_casm_from_path(  # pyright: ignore
            str(input_path),
            str(output_path) if output_path else None,
        )


def collect_tests(
    input_path: Path,
    output_path: Optional[Path] = None,
    cairo_path: Optional[list[Path]] = None,
) -> TestCollectorOutput:
    ensure_output_path(output_path=output_path)
    with handle_bindings_errors("collect_tests"):
        output = cairo_python_bindings.collect_tests(  # pyright: ignore
            str(input_path),
            str(output_path) if output_path else None,
            [str(path) for path in cairo_path] if cairo_path else None,
            RUNNER_BUILTINS_TITLE_CASE + ["GasBuiltin"],
        )
        return TestCollectorOutput(sierra_output=output[0], collected_tests=output[1])


def compile_protostar_sierra_to_casm_from_path(
    collected_tests: list[tuple[str, AvailableGas]],
    input_path: Path,
    output_path: Optional[Path] = None,
) -> Optional[dict]:
    ensure_output_path(output_path=output_path)
    with handle_bindings_errors("compile_protostar_sierra_to_casm_from_path"):
        compiled_str = cairo_python_bindings.compile_protostar_sierra_to_casm_from_path(  # pyright: ignore
            collected_tests, str(input_path), str(output_path) if output_path else None
        )
        return json.loads(compiled_str)


def compile_protostar_sierra_to_casm(
    named_tests: list[tuple[str, AvailableGas]],
    input_data: str,
    output_path: Optional[Path] = None,
) -> Optional[dict]:
    ensure_output_path(output_path=output_path)
    with handle_bindings_errors("compile_protostar_sierra_to_casm"):
        compiled_str = (
            cairo_python_bindings.compile_protostar_sierra_to_casm(  # pyright: ignore
                named_tests, input_data, str(output_path) if output_path else None
            )
        )
        return json.loads(compiled_str)


@contextmanager
def handle_bindings_errors(binding_name: str):
    try:
        yield
    except RuntimeError as ex:
        raise CairoBindingException(
            message=f"A runtime error occurred in binding {binding_name}: {str(ex)}"
        ) from ex
    except BaseException as ex:
        raise CairoBindingException(
            message=f"A unexpected type of error occurred in binding {binding_name}: {str(ex)}"
        ) from ex
