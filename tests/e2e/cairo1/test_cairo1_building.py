from pathlib import Path

import os

import pytest

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def test_cairo1_build(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")
    protostar(["build-cairo1"])
    compiled_sierra_path = Path("build/main.sierra.json")
    compiled_casm_path = Path("build/main.casm.json")
    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()


def test_cairo1_build_invalid_contract_path_to_cairo_file(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")

    protostar_toml = Path("protostar.toml")
    protostar_toml.write_text(
        protostar_toml.read_text().replace('main = ["src"]', 'main = ["src/lib.cairo"]')
    )
    with pytest.raises(Exception) as ex:
        protostar(["build-cairo1"])
    assert (
        "invalid input path: a directory path is expected, a file was received"
        in str(ex.value)
    )


def test_cairo1_build_invalid_contract_non_existent_path(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")

    protostar_toml = Path("protostar.toml")
    protostar_toml.write_text(
        protostar_toml.read_text().replace('main = ["src"]', 'main = ["srcc"]')
    )

    with pytest.raises(Exception) as ex:
        protostar(["build-cairo1"])
    assert "invalid input path: a directory path is expected" in str(ex.value)


def test_cairo1_build_invalid_contract_no_contract(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")

    lib_cairo = Path("src/lib.cairo")
    lib_cairo.write_text(lib_cairo.read_text().replace("#[contract]", ""))

    with pytest.raises(Exception) as ex:
        protostar(["build-cairo1"])
    assert "Contract not found" in str(ex.value)
