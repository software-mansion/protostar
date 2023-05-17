import os
from pathlib import Path

import pytest

from tests.e2e.conftest import ProtostarFixture


def test_init(protostar: ProtostarFixture):
    # Create a project
    protostar(["init", "myproject"])

    os.chdir("./myproject")
    protostar_toml_path = Path("protostar.toml")
    assert protostar_toml_path.exists()
    assert protostar_toml_path.read_text()

    # Assert contract is buildable
    result = protostar(["build"])
    compiled_sierra_path = Path("build/hello_starknet.sierra.json")
    compiled_casm_path = Path("build/hello_starknet.casm.json")
    assert compiled_sierra_path.exists()
    assert compiled_sierra_path.read_text()
    assert compiled_casm_path.exists()
    assert compiled_casm_path.read_text()

    # # Assert tests are running
    result = protostar(["test"])
    assert "Collected 2 suites, and 3 test cases" in result
    assert "3 passed" in result


@pytest.mark.parametrize(
    "project_name, error_reason",
    [
        ("_", "Project name cannot be equal to a single underscore."),
        ("8invalid", "Project name cannot start with a digit."),
        (
            "invalid-name",
            "Project name must use only ASCII alphanumeric characters or underscores.",
        ),
    ],
)
def test_init_with_invalid_name(
    protostar: ProtostarFixture, project_name: str, error_reason: str
):
    output = protostar(["init", project_name], expect_exit_code=1)
    assert error_reason + " Choose a different project name." in output


def test_init_without_name(protostar: ProtostarFixture):
    output = protostar(["init"], expect_exit_code=1)

    assert "project directory name: " in output


def test_init_fails_with_existing_folder(protostar: ProtostarFixture):
    project_name = "my_project"
    os.mkdir(project_name)

    output = protostar(["init", project_name], expect_exit_code=1)

    assert (
        f"Folder or file named {project_name} already exists. Choose different project name."
        in output
    )
