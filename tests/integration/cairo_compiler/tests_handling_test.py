from pathlib import Path
import pytest
from pytest_mock import MockerFixture

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.utils import RunResources

from protostar.cairo.cairo1_test_suite_parser import parse_test_suite
from protostar.cairo.cairo_bindings import (
    call_test_collector,
    call_protostar_sierra_to_casm_from_path,
)

from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.cairo_compiler.prepare_files_fixture import (
    PrepareFilesFixture,
    RequestedFile,
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
            RequestedFile.input_roll_test_cairo,
            RequestedFile.output_sierra,
            RequestedFile.output_casm,
        ]
    )

    test_collector_output = call_test_collector(
        prepared_files["input_roll_test_cairo"].path
    )
    assert test_collector_output.sierra_output and test_collector_output.test_names
    test_collector_output = call_test_collector(
        prepared_files["input_roll_test_cairo"].path,
        prepared_files["output_sierra"].path,
    )
    assert not test_collector_output.sierra_output and test_collector_output.test_names
    assert prepared_files["output_sierra"].path.read_text()

    protostar_casm_json = call_protostar_sierra_to_casm_from_path(
        test_collector_output.test_names,
        prepared_files["output_sierra"].path,
    )
    assert protostar_casm_json
    test_suite = parse_test_suite(
        Path(str(prepared_files["output_casm"].path)), protostar_casm_json
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
