from typing import Optional, Callable, Any
from pathlib import Path

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def extract_test_case_name(full_test_case_name: str):
    return full_test_case_name.split("::")[-1]


def get_mock_for_lib_func(
    lib_func_name: str,
    cairo_runner_facade: CairoRunnerFacade,
    test_case_name: str,
    err_code: Optional[int] = None,
    panic_data: Optional[list[int]] = None,
    args_validator: Optional[Callable] = None,
    return_values_provider: Optional[Callable] = None,
):
    if lib_func_name in ["declare", "declare_cairo0"]:
        assert return_values_provider
        ok = type(
            "ok",
            (object,),
            {"class_hash": return_values_provider(test_case_name)["class_hash"]},
        )()
        return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": ok}
        )()
    elif lib_func_name == "deploy_tp":
        assert return_values_provider
        ok = type(
            "ok",
            (object,),
            {
                "contract_address": return_values_provider(test_case_name)[
                    "contract_address"
                ]
            },
        )()
        return_value = type(
            "return_value", (object,), {"panic_data": panic_data, "ok": ok}
        )()
    elif lib_func_name == "call":
        assert return_values_provider
        ok = type(
            "ok",
            (object,),
            {"return_data": return_values_provider(test_case_name)["return_data"]},
        )()
        return_value = type(
            "return_value", (object,), {"panic_data": panic_data, "ok": ok}
        )()
    elif lib_func_name == "invoke":
        return_value = type(
            "return_value", (object,), {"panic_data": panic_data, "ok": None}
        )()
    elif lib_func_name == "prepare_tp":
        assert return_values_provider
        prepared_contract = type(
            "prepared_contract",
            (object,),
            {
                "constructor_calldata": return_values_provider(test_case_name)[
                    "constructor_calldata"
                ],
                "contract_address": return_values_provider(test_case_name)[
                    "contract_address"
                ],
                "class_hash": return_values_provider(test_case_name)["class_hash"],
            },
        )()
        return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": prepared_contract}
        )()
    else:
        return_value = type("return_value", (object,), {"err_code": err_code})()

    def mock(*args: Any, **kwargs: Any):
        if args_validator:
            assert cairo_runner_facade.current_runner
            args_validator(
                test_case_name,
                *args,
                **kwargs,
            )
        return return_value

    return mock


def compile_suite(cairo_test_path: Path) -> ProtostarCasm:
    test_collector_output = cairo1.collect_tests(input_path=cairo_test_path)
    assert test_collector_output.sierra_output
    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        named_tests=test_collector_output.collected_tests,
        input_data=test_collector_output.sierra_output,
    )
    assert protostar_casm_json
    return ProtostarCasm.from_json(protostar_casm_json)


REVERTABLE_FUNCTIONS = ["invoke", "call", "deploy_tp"]


def check_library_function(
    lib_func_name: str,
    cairo_test_path: Path,
    args_validator: Optional[Callable] = None,
    return_values_provider: Optional[Callable] = None,
):
    protostar_casm = compile_suite(cairo_test_path)
    for mocked_error_code in [0, 1, 50]:
        cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)
        for test_case_name, offset in protostar_casm.offset_map.items():
            err_code = None
            panic_data = []
            if lib_func_name in REVERTABLE_FUNCTIONS and mocked_error_code:
                panic_data.append(mocked_error_code)
            else:
                err_code = mocked_error_code

            cairo_runner_facade.run_from_offset(
                offset=offset,
                hint_locals={
                    lib_func_name: get_mock_for_lib_func(
                        lib_func_name=lib_func_name,
                        err_code=err_code,
                        panic_data=panic_data,
                        cairo_runner_facade=cairo_runner_facade,
                        test_case_name=test_case_name,
                        args_validator=args_validator,
                        return_values_provider=return_values_provider,
                    ),
                },
            )

            assert cairo_runner_facade.did_panic() == bool(mocked_error_code)


def test_roll(datadir: Path):
    check_library_function("roll", datadir / "roll_test.cairo")


def test_declare(datadir: Path):
    return_values = {"test_declare": {"class_hash": 123}}

    def _return_values_provider(test_case_name: str):
        return return_values[extract_test_case_name(test_case_name)]

    check_library_function(
        "declare",
        datadir / "declare_test.cairo",
        return_values_provider=_return_values_provider,
    )


def test_declare_cairo0(datadir: Path):
    return_values = {"test_declare_cairo0": {"class_hash": 123}}

    def _return_values_provider(test_case_name: str):
        return return_values[extract_test_case_name(test_case_name)]

    check_library_function(
        "declare_cairo0",
        datadir / "declare_cairo0_test.cairo",
        return_values_provider=_return_values_provider,
    )


def test_start_prank(datadir: Path):
    check_library_function("start_prank", datadir / "start_prank_test.cairo")


def test_stop_prank(datadir: Path):
    check_library_function("stop_prank", datadir / "stop_prank_test.cairo")


def test_warp(datadir: Path):
    check_library_function("warp", datadir / "warp_test.cairo")


def test_deploy(datadir: Path):
    expected_calldatas = {
        "test_deploy": [1, 2],
        "test_deploy_no_args": [],
        "test_deploy_tp": [5, 4, 2],
    }
    return_values = {
        "test_deploy": {"contract_address": 123},
        "test_deploy_no_args": {"contract_address": 4443},
        "test_deploy_tp": {"contract_address": 0},
    }

    def _args_validator(test_case_name: str, *args: Any, **kwargs: Any):
        assert not args
        assert kwargs["contract_address"] == 123 and kwargs["class_hash"] == 234
        expected_calldata = expected_calldatas[test_case_name.split("::")[-1]]
        assert expected_calldata == kwargs["constructor_calldata"]

    def _return_values_provider(test_case_name: str):
        return return_values[extract_test_case_name(test_case_name)]

    check_library_function(
        "deploy_tp",
        datadir / "deploy_test.cairo",
        args_validator=_args_validator,
        return_values_provider=_return_values_provider,
    )


def test_invoke(datadir: Path):
    expected_calldatas = {
        "test_invoke": [101, 202, 303, 405, 508, 613, 721],
        "test_invoke_no_args": [],
    }

    def _args_validator(test_case_name: str, *args: Any, **kwargs: Any):
        assert not args
        assert kwargs["contract_address"] == 123
        expected_calldata = expected_calldatas[extract_test_case_name(test_case_name)]
        assert expected_calldata == kwargs["calldata"]

    check_library_function(
        "invoke", datadir / "invoke_test.cairo", args_validator=_args_validator
    )


def test_prepare(datadir: Path):
    expected_calldatas = {
        "test_prepare": [101, 202, 613, 721],
        "test_prepare_tp": [3, 2, 1],
        "test_prepare_no_args": [],
    }
    return_values = {
        "test_prepare": {
            "constructor_calldata": [101, 202, 613, 721],
            "contract_address": 111,
            "class_hash": 222,
        },
        "test_prepare_tp": {
            "constructor_calldata": [3, 2, 1],
            "contract_address": 0,
            "class_hash": 444,
        },
        "test_prepare_no_args": {
            "constructor_calldata": [],
            "contract_address": 999,
            "class_hash": 345,
        },
    }

    def _args_validator(test_case_name: str, *args: Any, **kwargs: Any):
        assert not args
        assert kwargs["class_hash"] == 123
        expected_calldata = expected_calldatas[extract_test_case_name(test_case_name)]
        assert expected_calldata == kwargs["calldata"]

    def _return_values_provider(test_case_name: str):
        return return_values[extract_test_case_name(test_case_name)]

    check_library_function(
        "prepare_tp",
        datadir / "prepare_test.cairo",
        args_validator=_args_validator,
        return_values_provider=_return_values_provider,
    )


def test_mock_call(datadir: Path):
    expected_calldatas = {
        "test_mock_call": [121, 122, 123, 124],
        "test_mock_call_no_args": [],
    }

    def _args_validator(test_case_name: str, *args: Any, **kwargs: Any):
        assert not args
        assert kwargs["contract_address"] == 123
        expected_calldata = expected_calldatas[extract_test_case_name(test_case_name)]
        assert expected_calldata == kwargs["response"]

    check_library_function(
        "mock_call", datadir / "mock_call_test.cairo", args_validator=_args_validator
    )


def test_call(datadir: Path):
    expected_calldatas = {
        "test_call": [101, 613, 721, 508, 405],
        "test_call_no_args": [],
    }
    return_values = {
        "test_call": {"return_data": [3, 2, 5]},
        "test_call_no_args": {"return_data": []},
    }

    def _args_validator(test_case_name: str, *args: Any, **kwargs: Any):
        assert not args
        assert kwargs["contract_address"] == 123
        expected_calldata = expected_calldatas[extract_test_case_name(test_case_name)]
        assert expected_calldata == kwargs["calldata"]

    def _return_values_provider(test_case_name: str):
        return return_values[extract_test_case_name(test_case_name)]

    check_library_function(
        "call",
        datadir / "call_test.cairo",
        args_validator=_args_validator,
        return_values_provider=_return_values_provider,
    )


def test_deploy_contract(datadir: Path):
    protostar_casm = compile_suite(datadir / "deploy_contract_test.cairo")
    cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)

    for test_case_name, offset in protostar_casm.offset_map.items():
        cairo_runner_facade.run_from_offset(
            offset=offset,
            hint_locals={
                "declare": get_mock_for_lib_func(
                    lib_func_name="declare",
                    err_code=0,
                    cairo_runner_facade=cairo_runner_facade,
                    test_case_name=test_case_name,
                    return_values_provider=lambda _: {"class_hash": 123},  # type: ignore
                ),
                "prepare_tp": get_mock_for_lib_func(
                    lib_func_name="prepare_tp",
                    err_code=0,
                    cairo_runner_facade=cairo_runner_facade,
                    test_case_name=test_case_name,
                    return_values_provider=lambda _: {  # type: ignore
                        "constructor_calldata": [101, 202, 613, 721],
                        "contract_address": 111,
                        "class_hash": 123,
                    },
                ),
                "deploy_tp": get_mock_for_lib_func(
                    lib_func_name="deploy_tp",
                    err_code=0,
                    cairo_runner_facade=cairo_runner_facade,
                    test_case_name=test_case_name,
                    return_values_provider=lambda _: {"contract_address": 132},  # type: ignore
                ),
            },
        )
