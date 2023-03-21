from typing import Optional, Callable, Any
from pathlib import Path

from starkware.cairo.lang.vm.memory_dict import MemoryDict

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade
from protostar.starknet.data_transformer import CairoData


def get_mock_for_lib_func(
    lib_func_name: str,
    err_code: int,
    cairo_runner_facade: CairoRunnerFacade,
    test_case_name: str,
    args_validator: Optional[Callable] = None,
):
    if lib_func_name in ["declare", "declare_cairo0"]:
        ok = type("ok", (object,), {"class_hash": 0})()
        return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": ok}
        )()
    elif lib_func_name == "deploy_tp":
        ok = type("ok", (object,), {"deployed_contract_address": 0})()
        return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": ok}
        )()
    elif lib_func_name == "prepare_tp":
        prepared_contract = type(
            "prepared_contract",
            (object,),
            {
                "constructor_calldata": [],
                "contract_address": 0,
                "return_class_hash": 0,
            },
        )()
        ok = type("ok", (object,), {"prepared_contract": prepared_contract})()
        return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": ok}
        )()
    else:
        return_value = type("return_value", (object,), {"err_code": err_code})()

    def mock(*args: Any, **kwargs: Any):
        if args_validator:
            assert cairo_runner_facade.current_runner
            args_validator(
                cairo_runner_facade.current_runner.memory,
                test_case_name,
                *args,
                **kwargs,
            )
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
        for test_case_name, offset in protostar_casm.offset_map.items():
            cairo_runner_facade.run_from_offset(
                offset=offset,
                hint_locals={
                    lib_func_name: get_mock_for_lib_func(
                        lib_func_name=lib_func_name,
                        err_code=mocked_error_code,
                        cairo_runner_facade=cairo_runner_facade,
                        test_case_name=test_case_name,
                        args_validator=args_validator,
                    ),
                },
            )

            assert cairo_runner_facade.did_panic() == bool(mocked_error_code)


def test_roll(datadir: Path):
    check_library_function("roll", datadir / "roll_test.cairo")


def test_declare(datadir: Path):
    check_library_function("declare", datadir / "declare_test.cairo")


def test_declare_cairo0(datadir: Path):
    check_library_function("declare_cairo0", datadir / "declare_cairo0_test.cairo")


def test_start_prank(datadir: Path):
    check_library_function("start_prank", datadir / "start_prank_test.cairo")


def test_stop_prank(datadir: Path):
    check_library_function("stop_prank", datadir / "stop_prank_test.cairo")


def test_warp(datadir: Path):
    check_library_function("warp", datadir / "warp_test.cairo")


def test_deploy(datadir: Path):
    check_library_function("deploy_tp", datadir / "deploy_test.cairo")


def test_invoke(datadir: Path):
    expected_calldatas = {
        "test_invoke": [101, 202, 303, 405, 508, 613, 721],
        "test_invoke_no_args": [],
    }

    def _args_validator(
        memory: MemoryDict, test_case_name: str, *args: Any, **kwargs: Any
    ):
        assert not args
        contract_address = memory.data[kwargs["contract_address"][0]]
        assert contract_address == 123
        validate_calldata_arg(
            start_name="calldata_start",
            end_name="calldata_end",
            memory=memory,
            expected_calldata=expected_calldatas[test_case_name.split("::")[-1]],
            *args,
            **kwargs,
        )

    check_library_function(
        "invoke", datadir / "invoke_test.cairo", args_validator=_args_validator
    )


def test_prepare(datadir: Path):
    expected_calldatas = {
        "test_prepare": [101, 202, 303, 405, 508, 613, 721],
        "test_prepare_tp": [3, 2, 1],
        "test_prepare_no_args": [],
    }

    def _args_validator(
        memory: MemoryDict, test_case_name: str, *args: Any, **kwargs: Any
    ):
        assert not args
        class_hash = memory.data[kwargs["class_hash"][0]]
        assert class_hash == 123
        validate_calldata_arg(
            start_name="calldata_start",
            end_name="calldata_end",
            memory=memory,
            expected_calldata=expected_calldatas[test_case_name.split("::")[-1]],
            *args,
            **kwargs,
        )

    check_library_function(
        "prepare_tp", datadir / "prepare_test.cairo", args_validator=_args_validator
    )


def test_mock_call(datadir: Path):
    expected_calldatas = {
        "test_mock_call": [121, 122, 123, 124],
        "test_mock_call_no_args": [],
    }

    def _args_validator(
        memory: MemoryDict, test_case_name: str, *args: Any, **kwargs: Any
    ):
        assert not args
        contract_address = memory.data[kwargs["contract_address"][0]]
        assert contract_address == 123
        validate_calldata_arg(
            start_name="response_start",
            end_name="response_end",
            memory=memory,
            expected_calldata=expected_calldatas[test_case_name.split("::")[-1]],
            *args,
            **kwargs,
        )

    check_library_function(
        "mock_call", datadir / "mock_call_test.cairo", args_validator=_args_validator
    )


def validate_calldata_arg(
    start_name: str,
    end_name: str,
    memory: MemoryDict,
    expected_calldata: CairoData,
    *args: Any,
    **kwargs: Any,
):
    assert not args
    actual_calldata = []
    calldata_start = memory.data[kwargs[start_name][0]]
    calldata_end = memory.data[kwargs[end_name][0]]
    iterator = calldata_start
    while iterator != calldata_end:
        actual_calldata.append(memory.data[iterator])
        iterator = iterator + 1
    assert actual_calldata == expected_calldata
