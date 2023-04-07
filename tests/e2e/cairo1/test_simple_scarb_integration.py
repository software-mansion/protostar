import os

from tests.e2e.conftest import CopyFixture, ProtostarFixture


def test_cairo1_test_with_simple_scarb_integration(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("cairo1_scarb_integration", "./cairo1_scarb_integration")
    os.chdir("./cairo1_scarb_integration")

    result = protostar(["--no-color", "test-cairo1"])

    assert "Scarb.toml found, fetching Scarb packages" in result
    assert "Collected 1 suite, and 1 test case" in result
    assert "test_internal_dependencies" in result
    assert "1 passed, 1 total" in result
