from pathlib import Path

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def test_return_value(datadir: Path):
    builtins = ["pedersen", "bitwise"]
    test_collector_output = cairo1.collect_tests(
        input_path=datadir / "test.cairo", builtins=builtins
    )
    assert test_collector_output.sierra_output
    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        named_tests=test_collector_output.test_names,
        input_data=test_collector_output.sierra_output,
    )
    assert protostar_casm_json
    protostar_casm = ProtostarCasm.from_json(protostar_casm_json, builtins=builtins)
    cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)

    for _, offset in protostar_casm.offset_map.items():
        # this raises an error
        # Unknown value for memory cell at address 1:nnn.
        cairo_runner_facade.run_from_offset(offset=offset)

    assert not cairo_runner_facade.did_panic()
