import os
from tests.e2e.conftest import CopyFixture, ProtostarFixture


def test_testing(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "tests"])

    assert "Collected 3 suites, and 6 test cases" in result
    assert "6 passed" in result


def test_no_tests_found(protostar: ProtostarFixture):
    result = protostar(["test-cairo1", "tests"])

    assert "No test cases found" in result


def test_targeted_collecting(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "::test_B"])

    assert "Collected 1 suite, and 1 test case" in result
    assert "test_B" in result


def test_glob_collecting(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "./tests/**/*nested*::nested*"])

    assert "Collected 1 suite, and 2 test cases" in result
    assert "nested_1" in result
    assert "nested_2" in result


def test_ignoring_dir(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "./tests", "--ignore", "**/nested"])

    assert "nested_1" not in result
    assert "nested_2" not in result


def test_ignoring_cases(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "./tests", "--ignore", "**/*::*nested*"])

    assert "nested_1" not in result
    assert "nested_2" not in result
