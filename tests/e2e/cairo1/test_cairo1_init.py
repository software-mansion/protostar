import os
from pathlib import Path

from tests.e2e.conftest import ProtostarFixture


def test_init(protostar: ProtostarFixture):
    # Create a project
    protostar(["init-cairo1", "myproject"])

    os.chdir("./myproject")
    protostar_toml_path = Path("protostar.toml")
    assert protostar_toml_path.exists()
    assert protostar_toml_path.read_text()

    # Assert contract is buildable
    result = protostar(["build-cairo1"])
    compiled_path = Path("build/hello_starknet.json")
    assert compiled_path.exists()
    assert compiled_path.read_text()

    # # Assert tests are running
    result = protostar(["test-cairo1"])
    assert "Collected 2 suites, and 3 test cases" in result
    assert "3 passed" in result
