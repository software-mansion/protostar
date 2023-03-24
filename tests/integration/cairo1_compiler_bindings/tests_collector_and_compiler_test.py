from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from protostar.cairo.cairo1_test_suite_parser import ProtostarCasm
import protostar.cairo.cairo_bindings as cairo1
from protostar.cairo.cairo_function_runner_facade import CairoRunnerFacade


def test_compilator_and_parser(mocker: MockerFixture, datadir: Path):
    test_collector_output = cairo1.collect_tests(datadir / "roll_test.cairo")

    assert test_collector_output.sierra_output
    assert test_collector_output.named_tests == [
        "roll_test::roll_test::test_cheatcode_caller",
        "roll_test::roll_test::test_cheatcode_caller_twice",
        "roll_test::roll_test::test_cheatcode_caller_three",
    ]

    protostar_casm_json = cairo1.compile_protostar_sierra_to_casm(
        named_tests=[name for name, _ in test_collector_output.named_tests],
        input_data=test_collector_output.sierra_output,
        cairo_tests_configs=[config for _, config in test_collector_output.named_tests],
    )
    assert protostar_casm_json

    protostar_casm = ProtostarCasm.from_json(protostar_casm_json)

    cheat_mock = mocker.MagicMock()
    cheat_mock.return_value = type("return_value", (object,), {"err_code": 0})()
    # TODO https://github.com/software-mansion/protostar/issues/1434
    cairo_runner_facade = CairoRunnerFacade(program=protostar_casm.program)
    for offset in protostar_casm.offset_map.values():
        cairo_runner_facade.run_from_offset(offset, hint_locals={"roll": cheat_mock})

    assert cheat_mock.call_count == 6


def test_cairo_path_for_tests(datadir: Path, shared_datadir: Path):
    with pytest.raises(Exception):
        cairo1.collect_tests(input_path=datadir / "test_with_deps.cairo")

    with pytest.raises(Exception):
        cairo1.collect_tests(
            input_path=datadir / "test_with_deps.cairo",
            cairo_path=[shared_datadir / "external_lib_foo"],
        )

    result = cairo1.collect_tests(
        input_path=datadir / "test_with_deps.cairo",
        cairo_path=[
            shared_datadir / "external_lib_foo",
            shared_datadir / "external_lib_bar",
        ],
    )
    assert result.sierra_output
    assert result.named_tests == ["test_with_deps::test_with_deps::test_assert_true"]

    protostar_casm = cairo1.compile_protostar_sierra_to_casm(
        named_tests=[name for name, _ in result.named_tests],
        input_data=result.sierra_output,
        cairo_tests_configs=[config for _, config in result.named_tests],
    )
    assert protostar_casm
