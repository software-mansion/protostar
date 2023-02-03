from pathlib import Path
from typing import Optional

import cairo_python_bindings


def call_cairo_to_sierra_compiler(
    input_path: Path, output_path: Optional[Path] = None
) -> Optional[str]:
    return cairo_python_bindings.call_cairo_to_sierra_compiler(  # pyright: ignore
        str(input_path), str(output_path) if output_path else None
    )


def call_sierra_to_casm_compiler(
    input_path: Path, output_path: Optional[Path] = None
) -> Optional[str]:
    return cairo_python_bindings.call_sierra_to_casm_compiler(  # pyright: ignore
        str(input_path), str(output_path) if output_path else None
    )


def call_cairo_to_casm_compiler(
    input_path: Path, output_path: Optional[Path] = None
) -> Optional[str]:
    return cairo_python_bindings.call_cairo_to_casm_compiler(  # pyright: ignore
        str(input_path), str(output_path) if output_path else None
    )


def call_starknet_contract_compiler(
    input_path: Path, output_path: Optional[Path] = None
) -> Optional[str]:
    return cairo_python_bindings.call_starknet_contract_compiler(  # pyright: ignore
        str(input_path), str(output_path) if output_path else None
    )


def call_test_collector(
    input_path: Path,
    output_path: Optional[Path] = None,
    cairo_paths: Optional[list[Path]] = None,
) -> tuple[Optional[str], list[str]]:
    return cairo_python_bindings.call_test_collector(  # pyright: ignore
        str(input_path),
        str(output_path) if output_path else None,
        [str(path) for path in cairo_paths] if cairo_paths else None,
    )


def call_protostar_sierra_to_casm(
    named_tests: list[str], input_path: Path, output_path: Optional[Path] = None
) -> Optional[str]:
    return cairo_python_bindings.call_protostar_sierra_to_casm(  # pyright: ignore
        named_tests, str(input_path), str(output_path) if output_path else None
    )
