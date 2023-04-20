import os

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def execute_test(
    project_dir: str,
    test_name: str,
    test_path: str,
    protostar: ProtostarFixture,
    copy_fixture: CopyFixture,
):
    copy_fixture("scarb_integration/" + project_dir, "./" + project_dir)
    os.chdir("./" + project_dir)

    result = protostar(["--no-color", "test-cairo1", test_path])

    assert "Scarb.toml found, fetching Scarb packages" in result
    assert "Collected 1 suite, and 1 test case" in result
    assert test_name in result
    assert "1 passed, 1 total" in result
