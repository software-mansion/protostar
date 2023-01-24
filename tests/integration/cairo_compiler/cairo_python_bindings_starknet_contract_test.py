from pathlib import Path
import pytest

import cairo_python_bindings

from tests.data.contracts import (
    CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO,
    CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO_TEST,
)
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="prepared_files")
def prepared_files_fixture(protostar: ProtostarFixture):
    cairo_hello_path = Path("./src/hello.cairo")
    cairo_test_path = Path("./src/test.cairo")
    casm_path = Path("./src/example.casm")

    paths = {
        "cairo_hello": cairo_hello_path,
        "cairo_test": cairo_test_path,
        "casm": casm_path,
    }

    for _, path in paths.items():
        protostar.create_files({str(path): ""})
        assert path.exists()

    with open(cairo_hello_path, "w") as file:
        file.write(CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO)

    with open(cairo_test_path, "w") as file:
        file.write(CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO_TEST)

    return paths


def test_starknet_contract_compile(prepared_files: dict[str, Path]):
    def check_compile(contract_name: str):
        casm_contents = (
            cairo_python_bindings.call_starknet_contract_compiler(  # pyright: ignore
                str(prepared_files[contract_name])
            )
        )
        assert len(casm_contents)
        cairo_python_bindings.call_starknet_contract_compiler(  # pyright: ignore
            str(prepared_files[contract_name]), str(prepared_files["casm"])
        )
        assert prepared_files["casm"].exists() and prepared_files["casm"].stat().st_size
        with open(prepared_files["casm"], "r") as file:
            file_contents = file.readlines()
            assert len(casm_contents.split("\n")) >= len(file_contents)

    for contract_name in ["cairo_hello", "cairo_test"]:
        check_compile(contract_name=contract_name)
