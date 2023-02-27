from pathlib import Path
from pytest_mock import MockerFixture

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    ProtostarCasm,
)
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def get_mock_for_lib_func(mocker: MockerFixture, lib_func_name: str, err_code: int):
    if lib_func_name == "declare":
        declare_mock = mocker.MagicMock()
        ok = type("ok", (object,), {"class_hash": 0})()
        declare_mock.return_value = type(
            "return_value", (object,), {"err_code": err_code, "ok": ok}
        )()
        return declare_mock
    cheat_mock = mocker.MagicMock()
    cheat_mock.return_value = type("return_value", (object,), {"err_code": err_code})()
    return cheat_mock


def check_library_function(
    mocker: MockerFixture, lib_func_name: str, cairo_test_path: Path
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
                        mocker, lib_func_name, mocked_error_code
                    ),
                },
            )

            assert cairo_runner_facade.get_return_values(3)[0] == int(
                bool(mocked_error_code)
            )


def test_roll(mocker: MockerFixture, datadir: Path):
    check_library_function(mocker, "roll", datadir / "roll_test.cairo")


def test_declare(mocker: MockerFixture, datadir: Path):
    check_library_function(mocker, "declare", datadir / "declare_test.cairo")


def test_start_prank(mocker: MockerFixture, datadir: Path):
    check_library_function(mocker, "start_prank", datadir / "start_prank_test.cairo")
