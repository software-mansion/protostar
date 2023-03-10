import os
from pathlib import Path

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


def test_failing_tests(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    template_test_files = Path("cairo1_project/tests").glob("**/*")
    for template_test_file in template_test_files:
        template_test_file.unlink()
    copy_fixture("cairo1/failing_test.cairo", "./cairo1_project/tests")
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
