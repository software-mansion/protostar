from pathlib import Path
import pytest

from protostar.cairo.cairo_bindings import (
    call_test_collector,
    call_protostar_sierra_to_casm,
    call_cairo_to_casm_compiler,
    call_cairo_to_sierra_compiler,
    call_sierra_to_casm_compiler,
    call_starknet_contract_compiler,
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


SCRIPT_ROOT = Path(__file__).parent
CONTRACTS_DIR = SCRIPT_ROOT / "contracts"


def test_cairo_path_for_starknet_contract():
    casm_contents = call_starknet_contract_compiler(
        input_path=CONTRACTS_DIR / "starknet_project" / "basic_starknet_contract.cairo",
        cairo_paths=[CONTRACTS_DIR / "external_lib"],
    )
    assert casm_contents

    with pytest.raises(Exception):
        call_starknet_contract_compiler(
            input_path=CONTRACTS_DIR
            / "starknet_project"
            / "basic_starknet_contract.cairo",
        )


def test_cairo_path_for_starknet_test(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFile.output_sierra,
        ]
    )

    with pytest.raises(Exception):
        call_test_collector(input_path=CONTRACTS_DIR / "starknet_project")

    test_collector_output = call_test_collector(
        input_path=CONTRACTS_DIR / "starknet_project",
        output_path=prepared_files["output_sierra"].path,
        cairo_paths=[CONTRACTS_DIR / "external_lib"],
    )
    assert test_collector_output.test_names
    protostar_casm = call_protostar_sierra_to_casm(
        named_tests=test_collector_output.test_names,
        input_path=prepared_files["output_sierra"].path,
    )
    assert protostar_casm


def test_cairo_path_for_regular_compiler(prepare_files: PrepareFilesFixture):
    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFile.output_sierra,
        ]
    )

    # cairo -> sierra -> casm
    with pytest.raises(Exception):
        call_cairo_to_sierra_compiler(
            input_path=CONTRACTS_DIR / "regular_project" / "mycontract.cairo"
        )

    call_cairo_to_sierra_compiler(
        input_path=CONTRACTS_DIR / "regular_project" / "mycontract.cairo",
        output_path=prepared_files["output_sierra"].path,
        cairo_paths=[CONTRACTS_DIR / "external_lib"],
    )
    casm_contents = call_sierra_to_casm_compiler(
        input_path=prepared_files["output_sierra"].path,
    )
    assert casm_contents

    # cairo -> casm
    with pytest.raises(Exception):
        call_cairo_to_casm_compiler(
            input_path=CONTRACTS_DIR / "regular_project" / "mycontract.cairo"
        )

    casm_contents = call_cairo_to_casm_compiler(
        input_path=CONTRACTS_DIR / "regular_project" / "mycontract.cairo",
        cairo_paths=[CONTRACTS_DIR / "external_lib"],
    )
    assert casm_contents
