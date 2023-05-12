import os
import pytest

from tests.e2e.conftest import CopyFixture, ProtostarFixture


@pytest.mark.parametrize(
    "project_dir, test_name",
    (
        # contracts
        ("libraries", "contract_with_libraries_as_dependencies"),
        ("modules", "contract_with_modules_as_dependencies"),
        ("online_dependencies", "contract_with_online_repository_as_dependency"),
        ("multiple_contracts", "test_bar_func"),
        ("multiple_contracts", "test_foo_func"),
        # pure cairo
        ("libraries", "libraries_as_dependencies"),
        ("modules", "modules_as_dependencies"),
        ("online_dependencies", "online_repository_as_dependency"),
    ),
)
def test_testing_with_dependencies_using_scarb(
    project_dir: str,
    test_name: str,
    protostar: ProtostarFixture,
    copy_fixture: CopyFixture,
):
    copy_fixture("scarb_integration/" + project_dir, "./" + project_dir)
    os.chdir("./" + project_dir)

    result = protostar(["--no-color", "test", "::" + test_name])

    assert "Collected 1 suite, and 1 test case" in result
    assert test_name in result
    assert "1 passed, 1 total" in result
