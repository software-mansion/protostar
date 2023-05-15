from pathlib import Path

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def test_return_value(datadir: Path):
    test_collector_output = cairo1.collect_tests(
        input_path=datadir / "test.cairo",
        maybe_cairo_paths=[(datadir / "test.cairo", "test")],
    )
    assert test_collector_output.sierra_output
    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        named_tests=test_collector_output.collected_tests,
        input_data=test_collector_output.sierra_output,
    )
    assert protostar_casm_json
    protostar_casm = ProtostarCasm.from_json(protostar_casm_json)
    cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)

    assert len(protostar_casm.offset_map.items()) == 3
    for name, offset in protostar_casm.offset_map.items():
        cairo_runner_facade.run_from_offset(offset=offset)
        if name == "test::test::fibonacci_test_out_of_gas_panic":
            assert cairo_runner_facade.did_panic()
        else:
            assert not cairo_runner_facade.did_panic()
