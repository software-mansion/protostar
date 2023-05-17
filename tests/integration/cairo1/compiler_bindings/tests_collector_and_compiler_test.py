from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from protostar.cairo.cairo1_test_suite_parser import ProtostarCasm
import protostar.cairo.bindings.cairo_bindings as cairo1
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def test_compilator_and_parser(mocker: MockerFixture, datadir: Path):
    test_collector_output = cairo1.collect_tests(
        input_path=datadir / "start_roll_test.cairo",
        maybe_cairo_paths=[(datadir / "start_roll_test.cairo", "start_roll_test")],
    )

    assert test_collector_output.sierra_output
    assert test_collector_output.collected_tests == [
        ("start_roll_test::start_roll_test::test_cheatcode_caller", None),
        ("start_roll_test::start_roll_test::test_cheatcode_caller_twice", None),
        ("start_roll_test::start_roll_test::test_cheatcode_caller_three", None),
    ]

    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        test_collector_output.collected_tests, test_collector_output.sierra_output
    )
    assert protostar_casm_json

    protostar_casm = ProtostarCasm.from_json(protostar_casm_json)

    cheat_mock = mocker.MagicMock()
    cheat_mock.return_value = type("return_value", (object,), {"err_code": 0})()
    cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)
    for offset in protostar_casm.offset_map.values():
        cairo_runner_facade.run_from_offset(
            offset, hint_locals={"start_roll": cheat_mock}
        )

    assert cheat_mock.call_count == 6


def test_cairo_path_for_tests(datadir: Path, shared_datadir: Path):
    with pytest.raises(Exception):
        cairo1.collect_tests(
            input_path=datadir / "test_with_deps.cairo",
            maybe_cairo_paths=[(Path("no-dir"), "no-name")],
        )

    with pytest.raises(Exception):
        cairo1.collect_tests(
            input_path=datadir / "test_with_deps.cairo",
            maybe_cairo_paths=[
                (shared_datadir / "external_lib_foo", "external_lib_foo")
            ],
        )

    result = cairo1.collect_tests(
        input_path=datadir / "test_with_deps.cairo",
        maybe_cairo_paths=[
            (shared_datadir / "external_lib_foo", "external_lib_foo"),
            (shared_datadir / "external_lib_bar", "external_lib_bar"),
        ],
    )
    assert result.sierra_output
    assert result.collected_tests == [
        ("test_with_deps::test_with_deps::test_assert_true", None)
    ]

    protostar_casm = cairo1.compile_protostar_sierra_to_casm(
        result.collected_tests,
        result.sierra_output,
    )
    assert protostar_casm


def test_importing_from_contract(datadir: Path, shared_datadir: Path):
    result = cairo1.collect_tests(
        input_path=datadir / "test_with_contract_deps.cairo",
        maybe_cairo_paths=[
            (shared_datadir / "external_contract", "external_contract"),
        ],
    )

    assert result.sierra_output
    assert len(result.collected_tests) == 1
    assert (
        result.collected_tests[0][0]
        == "test_with_contract_deps::test_with_contract_deps::test_importing_from_contract"
    )
