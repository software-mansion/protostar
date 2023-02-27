from typing import Optional, Callable, Any
from pathlib import Path

from starkware.cairo.lang.vm.memory_dict import MemoryDict

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def get_mock_for_lib_func(
    lib_func_name: str,
    err_code: int,
    memory: MemoryDict,
    args_validator: Optional[Callable] = None,
):
    if lib_func_name == "declare":
        ok = type("ok", (object,), {"class_hash": 0})()
        return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": ok}
        )()
    else:
        return_value = type("return_value", (object,), {"err_code": err_code})()

    def mock(*args: Any, **kwargs: Any):
        if args_validator:
            args_validator(memory, *args, **kwargs)
        return return_value

    return mock


def check_library_function(
    lib_func_name: str, cairo_test_path: Path, args_validator: Optional[Callable] = None
):
    test_collector_output = cairo1.collect_tests(input_path=cairo_test_path)
    assert test_collector_output.sierra_output
    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        named_tests=test_collector_output.test_names,
        input_data=test_collector_output.sierra_output,
    )
    assert protostar_casm_json
    for mocked_error_code in [0, 1, 50]:
        protostar_casm = ProtostarCasm.from_json(protostar_casm_json)
        cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)
        for offset in protostar_casm.offset_map.values():
            cairo_runner_facade.run_from_offset(
                offset=offset,
                hint_locals={
                    lib_func_name: get_mock_for_lib_func(
                        lib_func_name=lib_func_name,
                        err_code=mocked_error_code,
                        memory=runner.vm_memory,
                        args_validator=args_validator,
                    ),
                },
            )

            assert cairo_runner_facade.get_return_values(3)[0] == int(
                bool(mocked_error_code)
            )


def test_roll(datadir: Path):
    check_library_function("roll", datadir / "roll_test.cairo")


def test_declare(datadir: Path):
    check_library_function("declare", datadir / "declare_test.cairo")


def test_start_prank(datadir: Path):
    check_library_function("start_prank", datadir / "start_prank_test.cairo")


def test_warp(datadir: Path):
    check_library_function("warp", datadir / "warp_test.cairo")


def test_invoke(datadir: Path):
    def args_validator(memory: MemoryDict, *args: Any, **kwargs: Any):
        assert not args
        contract_address = memory.data[kwargs["contract_address"][0]]
        assert contract_address == 123
        expected_calldata = [101, 202, 303, 405, 508, 613, 721]
        actual_calldata = []
        calldata_start = memory.data[kwargs["calldata_start"][0]]
        calldata_end = memory.data[kwargs["calldata_end"][0]]
        iterator = calldata_start
        while iterator != calldata_end:
            actual_calldata.append(memory.data[iterator])
            iterator = iterator + 1
        assert actual_calldata == expected_calldata

    check_library_function(
        "invoke", datadir / "invoke_test.cairo", args_validator=args_validator
    )
