import os

from tests.e2e.conftest import CopyFixture, ProtostarFixture


def test_cairo1_test_with_modules_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("scarb_integration/cairo1_scarb_modules", "./cairo1_scarb_modules")
    os.chdir("./cairo1_scarb_modules")

    result = protostar(["--no-color", "test-cairo1"])

    assert "Scarb.toml found, fetching Scarb packages" in result
    assert "Collected 1 suite, and 1 test case" in result
    assert "test_modules_as_dependencies" in result
    assert "1 passed, 1 total" in result


def test_cairo1_test_with_libraries_using_scarb(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("scarb_integration/cairo1_scarb_libraries", "./cairo1_scarb_libraries")
    os.chdir("./cairo1_scarb_libraries")

    result = protostar(["--no-color", "test-cairo1"])

    assert "Scarb.toml found, fetching Scarb packages" in result
    assert "Collected 1 suite, and 1 test case" in result
    assert "test_libraries_as_dependencies" in result
    assert "1 passed, 1 total" in result

# TODO: add test with external deps available online like quaireaux
