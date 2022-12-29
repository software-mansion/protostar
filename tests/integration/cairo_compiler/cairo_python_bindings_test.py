from pathlib import Path
import pytest

import cairo_python_bindings

from tests.data.contracts import CAIRO_BINDINGS_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


def test_basic(protostar: ProtostarFixture):
    cairo_path = Path("./src/example.cairo")
    sierra_path = Path("./src/example.sierra")
    casm_path = Path("./src/example.casm")

    for path in [cairo_path, sierra_path, casm_path]:
        protostar.create_files({str(path): ""})
        assert path.exists()

    with open(cairo_path, "w") as file:
        file.write(CAIRO_BINDINGS_CONTRACT)

    # cairo => sierra
    cairo_python_bindings.call_cairo_to_sierra_compiler(  # pyright: ignore
        str(cairo_path), str(sierra_path)
    )
    assert sierra_path.exists() and sierra_path.stat().st_size
    sierra_contents = (
        cairo_python_bindings.call_cairo_to_sierra_compiler(  # pyright: ignore
            str(cairo_path)
        )
    )
    assert len(sierra_contents)
    with open(sierra_path, "r") as file:
        file_contents = file.readlines()
        assert len(sierra_contents.split("\n")) >= len(file_contents)
    # sierra => casm
    cairo_python_bindings.call_sierra_to_casm_compiler(  # pyright: ignore
        str(sierra_path), str(casm_path)
    )
    assert casm_path.exists() and casm_path.stat().st_size
    casm_contents = (
        cairo_python_bindings.call_sierra_to_casm_compiler(  # pyright: ignore
            str(sierra_path)
        )
    )
    assert len(casm_contents)
    with open(casm_path, "r") as file:
        file_contents = file.readlines()
        assert len(casm_contents.split("\n")) >= len(file_contents)
