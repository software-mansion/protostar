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
    RequestedFiles,
)


@pytest.fixture(name="prepare_files")
def prepare_files_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        return PrepareFilesFixture(protostar)


def test_compilator_and_parser(
    prepare_files: PrepareFilesFixture, mocker: MockerFixture
):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.input_roll_test_cairo,
            RequestedFiles.output_sierra,
            RequestedFiles.output_casm,
        ]
    )

    sierra, named_tests = call_test_collector(  # pyright: ignore
        prepared_files["input_roll_test_cairo"][0],
    )
    assert sierra and named_tests
    _, named_tests = call_test_collector(  # pyright: ignore
        prepared_files["input_roll_test_cairo"][0],
        prepared_files["output_sierra"][0],
    )
    assert named_tests
    assert Path(prepared_files["output_sierra"][0]).read_text()

    protostar_casm_json = call_protostar_sierra_to_casm(  # pyright: ignore
        named_tests,
        prepared_files["output_sierra"][0],
    )
    assert protostar_casm_json
    test_suite = parse_test_suite(
        Path(str(prepared_files["output_casm"][0])), protostar_casm_json
    )
    cheat_mock = mocker.MagicMock()
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
