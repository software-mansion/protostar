import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import cairo_python_bindings


@dataclass
class TestCollectorOutput:
    sierra_output: Optional[str]
    test_names: list[str]


def compile_starknet_contract(
    input_path: Path,
    output_path: Optional[Path] = None,
    cairo_path: Optional[list[Path]] = None,
) -> Optional[str]:
    return cairo_python_bindings.call_starknet_contract_compiler(  # pyright: ignore
        str(input_path),
        str(output_path) if output_path else None,
        [str(path) for path in cairo_path] if cairo_path else None,
    )


def collect_tests(
    input_path: Path,
    output_path: Optional[Path] = None,
    cairo_path: Optional[list[Path]] = None,
) -> TestCollectorOutput:
    output = cairo_python_bindings.call_test_collector(  # pyright: ignore
        str(input_path),
        str(output_path) if output_path else None,
        [str(path) for path in cairo_path] if cairo_path else None,
    )
    return TestCollectorOutput(sierra_output=output[0], test_names=output[1])


def compile_protostar_sierra_to_casm_from_path(
    named_tests: list[str], input_path: Path, output_path: Optional[Path] = None
) -> Optional[dict]:
    compiled_str = cairo_python_bindings.call_protostar_sierra_to_casm_from_path(  # pyright: ignore
        named_tests, str(input_path), str(output_path) if output_path else None
    )
    return json.loads(compiled_str)


def compile_protostar_sierra_to_casm(
    named_tests: list[str], input_data: str, output_path: Optional[Path] = None
) -> Optional[dict]:
    compiled_str = (
        cairo_python_bindings.call_protostar_sierra_to_casm(  # pyright: ignore
            named_tests, input_data, str(output_path) if output_path else None
        )
    )
    return json.loads(compiled_str)
