from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources

from protostar.cairo.cairo1_test_suite_parser import parse_test_suite
from protostar.cairo.cairo_bindings import (
    call_test_collector,
    call_protostar_sierra_to_casm,
)

from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.cairo_compiler.prepare_files_fixture import (
    PrepareFilesFixture,
)


@pytest.fixture(name="prepare_files")
def prepare_files_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        return PrepareFilesFixture(protostar)


def test_compilator_and_parser(
   mocker: MockerFixture, datadir: Path
):
    test_collector_output = call_test_collector(
        datadir / "roll_test.cairo"
    )

    assert test_collector_output.sierra_output
    assert test_collector_output.test_names == ["roll_test::roll_test::test_cheatcode_caller", "roll_test::roll_test::test_cheatcode_caller_twice", "roll_test::roll_test::test_cheatcode_caller_three"]

    protostar_casm_json = call_protostar_sierra_to_casm(
        test_collector_output.test_names,
        test_collector_output.sierra_output
    )
    assert protostar_casm_json

    test_suite = parse_test_suite(
        datadir / "roll_test.cairo", protostar_casm_json
    )

    cheat_mock = mocker.MagicMock()
    cheat_mock.return_value = 0
    # TODO https://github.com/software-mansion/protostar/issues/1434
    for case in test_suite.test_cases:
        runner = CairoFunctionRunner(program=test_suite.program, layout="all")
        runner.run_from_entrypoint(
            case.offset,
            *[],
            hint_locals={"roll": cheat_mock},
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
    assert cheat_mock.call_count == 6
