import pytest

from protostar.cairo.cairo_bindings import (
    call_cairo_to_casm_compiler,
    call_cairo_to_sierra_compiler,
    call_sierra_to_casm_compiler,
)

from tests.integration.conftest import CreateProtostarProjectFixture

from tests.integration.cairo_compiler.prepare_files_fixture import (
    PrepareFilesFixture,
    RequestedFile,
    check_compiler_function,
)


@pytest.fixture(name="prepare_files")
def prepare_files_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        return PrepareFilesFixture(protostar)


def test_cairo_to_sierra_to_casm(prepare_files: PrepareFilesFixture):
    input_contract = RequestedFile.input_enum_contract_cairo
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            input_contract,
            RequestedFile.output_sierra,
            RequestedFile.output_casm,
        ]
    )

    check_compiler_function(
        call_cairo_to_sierra_compiler,
        prepared_files[input_contract.name].path,
        prepared_files["output_sierra"].path,
    )
    check_compiler_function(
        call_sierra_to_casm_compiler,
        prepared_files["output_sierra"].path,
        prepared_files["output_casm"].path,
    )
    # call_cairo_to_casm_compiler = call_cairo_to_sierra_compiler + call_sierra_to_casm_compiler
    check_compiler_function(
        call_cairo_to_casm_compiler,
        prepared_files[input_contract.name].path,
        prepared_files["output_casm"].path,
    )
