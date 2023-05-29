import os
import pytest

from tests.e2e.conftest import CopyFixture, ProtostarFixture


def test_cairo1_rust_test(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture("cairo1/test_a.cairo", "./cairo1_project/tests/test_a.cairo")
    os.chdir("./cairo1_project")

    result = protostar(["test-rust", "tests/test_a.cairo"])

    assert "test_A: Success" in result
    assert "test_B: Success" in result
    assert "test_C: Success" in result


def test_no_tests_provided(protostar: ProtostarFixture):
    with pytest.raises(Exception) as ex:
        protostar(["test-rust"])
    assert "No tests provided" in str(ex)


def test_no_tests_found(protostar: ProtostarFixture):
    with pytest.raises(Exception) as ex:
        protostar(["test-rust", "tests"])

    assert "no such test: tests" in str(ex.value)


def test_failing_tests(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_project", "./cairo1_project")
    copy_fixture(
        "cairo1/failing_test.cairo", "./cairo1_project/tests/failing_test.cairo"
    )
    os.chdir("./cairo1_project")

    result = protostar(["test-rust", "tests/failing_test.cairo"])
    assert "test_ok: Success" in result
    assert "test_panic_single_value: Panic [21]" in result
    assert (
        "test_panic_multiple_values: Panic [1870930782904301745253, 482670963043, 31066316372818838395891839589]"
        in result
    )


def test_declare(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("cairo1_build", "./cairo1_project")
    copy_fixture(
        "cairo1/declare_test.cairo", "./cairo1_project/tests/declare_test.cairo"
    )
    os.chdir("./cairo1_project")

    result = protostar(["test-rust", "tests/declare_test.cairo"])
    print()
    print("============================================ RESULT")
    print(result)
    print("============================================")
