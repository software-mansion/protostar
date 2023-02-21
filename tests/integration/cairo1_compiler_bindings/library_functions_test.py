from pathlib import Path
from pytest_mock import MockerFixture

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources

import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo1_test_suite_parser import (
    program_from_casm,
    get_test_name_to_offset_map_from_casm,
)


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
        program = program_from_casm(protostar_casm_json)
        test_name_to_offset = get_test_name_to_offset_map_from_casm(protostar_casm_json)

        for offset in test_name_to_offset.values():
            runner = CairoFunctionRunner(program, layout="all")
            runner.run_from_entrypoint(
                offset,
                *[],
                hint_locals={
                    lib_func_name: get_mock_for_lib_func(
                        mocker, lib_func_name, mocked_error_code
                    ),
                },
                static_locals={
                    "__find_element_max_size": 2**20,
                    "__squash_dict_max_size": 2**20,
                    "__keccak_max_size": 2**20,
                    "__usort_max_size": 2**20,
                    "__chained_ec_op_max_len": 1000,
                },
                run_resources=RunResources(n_steps=100000000000000000),
                verify_secure=False,
            )
            assert runner.get_return_values(3)[0] == int(bool(mocked_error_code))


def test_roll(mocker: MockerFixture, datadir: Path):
    check_library_function(mocker, "roll", datadir / "roll_test.cairo")


def test_declare(mocker: MockerFixture, datadir: Path):
    check_library_function(mocker, "declare", datadir / "declare_test.cairo")


def test_start_prank(mocker: MockerFixture, datadir: Path):
    check_library_function(mocker, "start_prank", datadir / "start_prank_test.cairo")
