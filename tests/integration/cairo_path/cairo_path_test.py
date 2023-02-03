from pathlib import Path
import pytest

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


SCRIPT_ROOT = Path(__file__).parent


def test_cairo_path_for_starknet_compiler(prepare_files: PrepareFilesFixture):
    contracts_dir = SCRIPT_ROOT / "contracts"

    prepared_files = prepare_files.prepare_files(
        requested_files=[
            RequestedFiles.output_sierra,
        ]
    )

    _, test_names = call_test_collector(
        input_path=contracts_dir / "main_project",
        output_path=prepared_files["output_sierra"][0],
        cairo_paths=[contracts_dir / "external_lib"],
    )
    assert test_names
    protostar_casm = call_protostar_sierra_to_casm(
        named_tests=test_names,
        input_path=prepared_files["output_sierra"][0],
    )
    assert protostar_casm
