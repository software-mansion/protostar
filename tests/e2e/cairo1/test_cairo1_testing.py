import os

from tests.e2e.conftest import CopyFixture, ProtostarFixture


def test_testing(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture("cairo1/test_a.cairo", "./cairo1_project/tests/test_a.cairo")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "tests"])

    assert "Collected 1 suite, and 3 test cases" in result
    assert "3 passed" in result


def test_no_tests_found(protostar: ProtostarFixture):
    result = protostar(["test-cairo1", "tests"])

    assert "No test cases found" in result


def test_failing_tests(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture(
        "cairo1/failing_test.cairo", "./cairo1_project/tests/failing_test.cairo"
    )
    os.chdir("./cairo1_project")

    result = protostar(["--no-color", "test-cairo1", "tests"], ignore_exit_code=True)

    expected_output_lines = [
        "Collected 1 suite, and 3 test cases",
        "[PASS] tests/failing_test.cairo test_ok",
        "[FAIL] tests/failing_test.cairo test_panic_multiple_values",
        "Test failed with data: [101, 102, 103]",
        "[FAIL] tests/failing_test.cairo test_panic_single_value",
        "Test failed with data: [21]",
        "1 failed, 1 total",
        "2 failed, 1 passed, 3 total",
    ]

    for expected_output_line in expected_output_lines:
        assert expected_output_line in result


def test_targeted_collecting(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture("cairo1/test_a.cairo", "./cairo1_project/tests/test_a.cairo")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "::test_B"])

    assert "Collected 1 suite, and 1 test case" in result
    assert "test_B" in result


def test_glob_collecting(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture("cairo1/nested", "./cairo1_project/tests/nested")
    os.chdir("./cairo1_project")

    result = protostar(["test-cairo1", "./tests/**/*nested*::nested*"])

    assert "Collected 1 suite, and 2 test cases" in result
    assert "nested_1" in result
    assert "nested_2" in result


def test_ignoring_dir(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture("cairo1/test_a.cairo", "./cairo1_project/tests/test_a.cairo")
    copy_fixture("cairo1/nested", "./cairo1_project/tests/nested")

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


def test_exit_first(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture("cairo1/failing_test.cairo", "./cairo1_project/tests")
    os.chdir("./cairo1_project")

    result = protostar(
        ["--no-color", "test-cairo1", "--exit-first", "./tests"], ignore_exit_code=True
    )
    # The test suite contains 2 failing tests, so it should fail only one of them when using exit-first
    assert "1 failed" in result
