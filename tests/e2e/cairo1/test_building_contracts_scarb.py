import os
from pathlib import Path

import pytest

from tests.e2e.conftest import ProtostarFixture, CopyFixture


@pytest.mark.parametrize(
    "project_directory", ("libraries", "modules", "online_dependencies")
)
def test_build_with_dependencies_using_scarb(
    project_directory: str, protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("scarb_integration/" + project_directory, "./" + project_directory)
    os.chdir("./" + project_directory)

    result = protostar(["--no-color", "build-cairo1"])

    assert "Contracts built successfully" in result

    compiled_sierra_path = Path("build/contract.sierra.json")
    compiled_casm_path = Path("build/contract.casm.json")

    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()


def test_build_multiple_contracts_with_dependencies_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("scarb_integration/multiple_contracts", "./multiple_contracts")
    os.chdir("./multiple_contracts")

    result = protostar(["--no-color", "build-cairo1"])

    assert "Contracts built successfully" in result

    compiled_sierra_path = Path("build/contract_foo.sierra.json")
    compiled_casm_path = Path("build/contract_foo.casm.json")

    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()

    compiled_sierra_path = Path("build/contract_bar.sierra.json")
    compiled_casm_path = Path("build/contract_bar.casm.json")

    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()
