import os
from pathlib import Path

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def test_build_with_libraries_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_build_test("libraries", protostar, copy_fixture)


def test_build_with_modules_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_build_test("modules", protostar, copy_fixture)


# TODO #1767: investigate differences in gas support between quaireaux and protostar
#  building works for some reason even considering the differences mentioned above...
def test_build_with_online_dependencies_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    execute_build_test("online_dependencies", protostar, copy_fixture)


def execute_build_test(
    path: str, protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("scarb_integration/" + path, "./" + path)
    os.chdir("./" + path)

    result = protostar(["--no-color", "build-cairo1"])

    assert "Scarb.toml found, fetching Scarb packages" in result
    assert "Contracts built successfully" in result

    compiled_sierra_path = Path("build/contract.sierra.json")
    compiled_casm_path = Path("build/contract.casm.json")

    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()
