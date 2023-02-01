import pytest

from protostar.cairo.cairo_bindings import (
    call_starknet_contract_compiler,
)

from tests.integration.conftest import CreateProtostarProjectFixture

from tests.integration.cairo_compiler.prepare_files_fixture import (
    PrepareFilesFixture,
    RequestedFiles,
    check_compiler_function,
)


@pytest.fixture(name="prepare_files")
def prepare_files_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        return PrepareFilesFixture(protostar)


def test_cairo_to_sierra_to_casm(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.input_simple_starknet_contract_cairo,
            RequestedFiles.input_simple_starknet_test_cairo,
            RequestedFiles.output_casm,
        ]
    )

    check_compiler_function(
        call_starknet_contract_compiler,
        prepared_files["input_simple_starknet_contract_cairo"][0],
        prepared_files["output_casm"][0],
    )
    check_compiler_function(
        call_starknet_contract_compiler,
        prepared_files["input_simple_starknet_test_cairo"][0],
        prepared_files["output_casm"][0],
    )
