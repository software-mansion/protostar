import os
from pathlib import Path

import pytest

from tests.e2e.conftest import ProtostarFixture, CopyFixture


# TODO #1767: investigate differences in gas support between quaireaux and protostar ("online_dependencies")
#  building works for some reason even considering the differences mentioned above...
@pytest.mark.parametrize(
    "project_directory", ("libraries", "modules", "online_dependencies")
)
def test_build_with_dependencies_using_scarb(
    project_directory: str, protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("scarb_integration/" + project_directory, "./" + project_directory)
    os.chdir("./" + project_directory)

    result = protostar(["--no-color", "build-cairo1"])

    assert "Scarb.toml found, fetching Scarb packages" in result
    assert "Contracts built successfully" in result

    compiled_sierra_path = Path("build/contract.sierra.json")
    compiled_casm_path = Path("build/contract.casm.json")

    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()
