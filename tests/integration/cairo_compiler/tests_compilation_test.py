from pathlib import Path
import pytest

from protostar.cairo.cairo_bindings import (
    call_test_collector,
    call_protostar_sierra_to_casm,
    call_cairo_to_casm_compiler,
    call_cairo_to_sierra_compiler,
    call_sierra_to_casm_compiler,
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


def test_tests_collector(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.input_test_cairo,
            RequestedFiles.output_sierra,
            RequestedFiles.output_casm,
        ]
    )
    sierra, named_tests = call_test_collector(  # pyright: ignore
        prepared_files["input_test_cairo"][0],
    )
    assert sierra and named_tests
    _, named_tests = call_test_collector(  # pyright: ignore
        prepared_files["input_test_cairo"][0],
        prepared_files["output_sierra"][0],
    )
    assert named_tests
    assert Path(prepared_files["output_sierra"][0]).read_text()

    protostar_casm_json = call_protostar_sierra_to_casm(  # pyright: ignore
        named_tests,
        prepared_files["output_sierra"][0],
    )
    assert protostar_casm_json
    call_protostar_sierra_to_casm(  # pyright: ignore
        named_tests,
        prepared_files["output_sierra"][0],
        prepared_files["output_casm"][0],
    )
    assert Path(prepared_files["output_casm"][0]).read_text()


def test_cairo_to_casm(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.input_test_cairo,
            RequestedFiles.input_contract_cairo,
            RequestedFiles.output_casm,
        ]
    )

    def check_compilation(name: str):
        call_cairo_to_casm_compiler(  # pyright: ignore
            prepared_files[name][0], prepared_files["output_casm"][0]
        )
        assert (
            prepared_files["output_casm"][0].exists()
            and prepared_files["output_casm"][0].stat().st_size
        )
        casm_contents = call_cairo_to_casm_compiler(  # pyright: ignore
            prepared_files[name][0]
        )
        assert casm_contents
        with open(prepared_files["output_casm"][0], "r") as file:
            file_contents = file.readlines()
            assert len(casm_contents.split("\n")) >= len(file_contents)

    for name in ["input_contract_cairo", "input_test_cairo"]:
        check_compilation(name=name)


def test_cairo_to_sierra_to_casm(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.input_test_cairo,
            RequestedFiles.input_contract_cairo,
            RequestedFiles.output_sierra,
            RequestedFiles.output_casm,
        ]
    )

    def check_compilation(name: str):
        # cairo => sierra
        call_cairo_to_sierra_compiler(  # pyright: ignore
            prepared_files[name][0], prepared_files["output_sierra"][0]
        )
        assert (
            prepared_files["output_sierra"][0].exists()
            and prepared_files["output_sierra"][0].stat().st_size
        )
        sierra_contents = call_cairo_to_sierra_compiler(  # pyright: ignore
            prepared_files[name][0]
        )
        assert sierra_contents
        with open(prepared_files["output_sierra"][0], "r") as file:
            file_contents = file.readlines()
            assert len(sierra_contents.split("\n")) >= len(file_contents)
        # sierra => casm
        call_sierra_to_casm_compiler(  # pyright: ignore
            prepared_files["output_sierra"][0],
            prepared_files["output_casm"][0],
        )
        assert (
            prepared_files["output_casm"][0].exists()
            and prepared_files["output_casm"][0].stat().st_size
        )
        casm_contents = call_sierra_to_casm_compiler(  # pyright: ignore
            prepared_files["output_sierra"][0]
        )
        assert casm_contents
        with open(prepared_files["output_casm"][0], "r") as file:
            file_contents = file.readlines()
            assert len(casm_contents.split("\n")) >= len(file_contents)

    for name in ["input_contract_cairo", "input_test_cairo"]:
        check_compilation(name=name)
