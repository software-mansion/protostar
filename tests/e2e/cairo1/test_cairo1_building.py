import json
import os
from pathlib import Path

import pytest

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def test_cairo1_build(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")

    result = protostar(["build"])

    assert 'Class hash for contract "main": 0x' in result
    assert 'Compiled class hash for contract "main": 0x' in result

    compiled_sierra_path = Path("build/main.sierra.json")
    compiled_casm_path = Path("build/main.casm.json")
    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()

    class_hash_path = Path("build/main.class_hash")
    compiled_class_hash_path = Path("build/main.compiled_class_hash")
    assert class_hash_path.exists()
    assert class_hash_path.read_text().startswith("0x")
    assert compiled_class_hash_path.exists()
    assert compiled_class_hash_path.read_text().startswith("0x")


def test_cairo1_build_json(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")
    result_json = protostar(["build", "--json"], ignore_stderr=True)

    output_json_parsed = json.loads(result_json.split("\n")[0])

    assert output_json_parsed["main"]["class_hash"].startswith("0x")
    assert output_json_parsed["main"]["compiled_class_hash"].startswith("0x")


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
        protostar(["build"])
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
        protostar(["build"])
    assert "invalid input path: a directory path is expected" in str(ex.value)


def test_cairo1_build_invalid_contract_no_contract(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo1_build", "./cairo_project")
    os.chdir("./cairo_project")

    lib_cairo = Path("src/lib.cairo")
    lib_cairo.write_text(lib_cairo.read_text().replace("#[contract]", ""))

    with pytest.raises(Exception) as ex:
        protostar(["build"])
    assert "Contract not found" in str(ex.value)
