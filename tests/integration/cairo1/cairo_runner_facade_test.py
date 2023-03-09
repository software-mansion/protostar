from pathlib import Path

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def test_return_value(datadir: Path):
    test_collector_output = cairo1.collect_tests(input_path=datadir / "test.cairo")
    assert test_collector_output.sierra_output
    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        named_tests=test_collector_output.test_names,
        input_data=test_collector_output.sierra_output,
    )
    assert protostar_casm_json
    protostar_casm = ProtostarCasm.from_json(protostar_casm_json)
    cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)

    expected_outcome = {
        "test::test::test_ok": {
            "did_panic": False,
            "panic_data": [],
        },
        "test::test::test_panic_single_value": {
            "did_panic": True,
            "panic_data": [21],
        },
        "test::test::test_panic_multiple_values": {
            "did_panic": True,
            "panic_data": [101, 102, 103],
        },
    }
    actual_outcome = {}
    for test_case_name, offset in protostar_casm.offset_map.items():
        cairo_runner_facade.run_from_offset(offset=offset)
        actual_outcome[test_case_name] = {
            "did_panic": cairo_runner_facade.did_panic(),
            "panic_data": cairo_runner_facade.get_panic_data(),
        }
    assert actual_outcome == expected_outcome
