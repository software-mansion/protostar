import os
from pathlib import Path
import pytest

import cairo_python_bindings

from tests.data.contracts import CAIRO_BINDINGS_CONTRACT
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
        file.write(CAIRO_BINDINGS_CONTRACT)

    return paths


def test_cairo_to_casm(protostar: ProtostarFixture, prepared_files: dict[str, Path]):
    cairo_python_bindings.call_cairo_to_casm_compiler(  # pyright: ignore
        str(prepared_files["cairo"]), str(prepared_files["casm"])
    )
    assert prepared_files["casm"].exists() and prepared_files["casm"].stat().st_size
    casm_contents = (
        cairo_python_bindings.call_cairo_to_casm_compiler(  # pyright: ignore
            str(prepared_files["cairo"])
        )
    )
    assert len(casm_contents)
    with open(prepared_files["casm"], "r") as file:
        file_contents = file.readlines()
        assert len(casm_contents.split("\n")) >= len(file_contents)


def test_cairo_to_sierra_to_casm(
    protostar: ProtostarFixture, prepared_files: dict[str, Path]
):
    # cairo => sierra
    cairo_python_bindings.call_cairo_to_sierra_compiler(  # pyright: ignore
        str(prepared_files["cairo"]), str(prepared_files["sierra"])
    )
    assert prepared_files["sierra"].exists() and prepared_files["sierra"].stat().st_size
    sierra_contents = (
        cairo_python_bindings.call_cairo_to_sierra_compiler(  # pyright: ignore
            str(prepared_files["cairo"])
        )
    )
    assert len(sierra_contents)
    with open(prepared_files["sierra"], "r") as file:
        file_contents = file.readlines()
        assert len(sierra_contents.split("\n")) >= len(file_contents)
    # sierra => casm
    cairo_python_bindings.call_sierra_to_casm_compiler(  # pyright: ignore
        str(prepared_files["sierra"]), str(prepared_files["casm"])
    )
    assert prepared_files["casm"].exists() and prepared_files["casm"].stat().st_size
    casm_contents = (
        cairo_python_bindings.call_sierra_to_casm_compiler(  # pyright: ignore
            str(prepared_files["sierra"])
        )
    )
    assert len(casm_contents)
    with open(prepared_files["casm"], "r") as file:
        file_contents = file.readlines()
        assert len(casm_contents.split("\n")) >= len(file_contents)
