import pytest

from protostar.cairo.cairo_bindings import call_starknet_contract_compiler

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


def test_starknet_contract_compile(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.input_simple_contract_cairo,
            RequestedFiles.input_simple_test_cairo,
            RequestedFiles.output_casm,
        ]
    )

    def check_compile(contract_name: str):
        casm_contents = call_starknet_contract_compiler(  # pyright: ignore
            prepared_files[contract_name][0]
        )
        assert casm_contents
        call_starknet_contract_compiler(  # pyright: ignore
            prepared_files[contract_name][0], prepared_files["output_casm"][0]
        )
        assert (
            prepared_files["output_casm"][0].exists()
            and prepared_files["output_casm"][0].stat().st_size
        )
        with open(prepared_files["output_casm"][0], "r") as file:
            file_contents = file.readlines()
            assert len(casm_contents.split("\n")) >= len(file_contents)

    for contract_name_item in ["input_hello_contract_cairo", "input_hello_test_cairo"]:
        check_compile(contract_name=contract_name_item)
