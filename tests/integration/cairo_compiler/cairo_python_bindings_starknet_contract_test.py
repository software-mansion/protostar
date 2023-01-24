from pathlib import Path
import pytest

import cairo_python_bindings

from tests.data.contracts import CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="prepared_files")
def prepared_files_fixture(protostar: ProtostarFixture):
    cairo_path = Path("./src/example.cairo")
    sierra_path = Path("./src/example.sierra")
    casm_path = Path("./src/example.casm")

    paths = {"cairo": cairo_path, "sierra": sierra_path, "casm": casm_path}

    for _, path in paths.items():
        protostar.create_files({str(path): ""})
        assert path.exists()

    with open(cairo_path, "w") as file:
        file.write(CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO)

    return paths


def test_starknet_contract_compile(prepared_files: dict[str, Path]):
    casm_contents = (
        cairo_python_bindings.call_starknet_contract_compiler(  # pyright: ignore
            str(prepared_files["cairo"])
        )
    )
    assert len(casm_contents)
    cairo_python_bindings.call_starknet_contract_compiler(  # pyright: ignore
        str(prepared_files["cairo"]), str(prepared_files["casm"])
    )
    assert prepared_files["casm"].exists() and prepared_files["casm"].stat().st_size
    with open(prepared_files["casm"], "r") as file:
        file_contents = file.readlines()
        assert len(casm_contents.split("\n")) >= len(file_contents)
