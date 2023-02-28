import os
from tests.e2e.conftest import CopyFixture, ProtostarFixture


def test_testing(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "tests"])

    assert "Collected 2 suites, and 4 test cases" in result
    assert "4 passed" in result


def test_no_tests_found(protostar: ProtostarFixture):
    result = protostar(["test-cairo1", "tests"])

    assert "No test cases found" in result
