import shutil
from subprocess import CalledProcessError

import pytest

from tests.e2e.conftest import ACTUAL_CWD, ProtostarFixture


@pytest.mark.usefixtures("init")
def test_basic_contract(protostar):
    result = protostar(["test", "tests"])
    assert "1 passed" in result


@pytest.mark.usefixtures("init")
def test_safe_collecting(protostar):
    result = protostar(["test", "--safe-collecting"])
    assert "1 passed" in result

@pytest.mark.usefixtures("init")
def test_complex(protostar, copy_fixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")

    result = protostar(["test", "tests"])

    assert "Collected 2 suites, and 4 test cases" in result
    assert "4 passed" in result


@pytest.mark.usefixtures("init")
def test_expect_revert(protostar):
    shutil.copy(
        ACTUAL_CWD
        / "tests"
        / "integration"
        / "cheatcodes"
        / "expect_revert"
        / "expect_revert_test.cairo",
        "./tests",
    )

    result = protostar(
        ["--no-color", "test", "tests/expect_revert_test.cairo"], ignore_exit_code=True
    )

    assert "[PASS] tests/expect_revert_test.cairo test_error_message" in result
    assert "[PASS] tests/expect_revert_test.cairo test_partial_error_message" in result
    assert "[FAIL] tests/expect_revert_test.cairo test_fail_error_message" in result
    assert (
        "[FAIL] tests/expect_revert_test.cairo test_with_except_revert_fail_expected"
        in result
    )
    assert "[PASS] tests/expect_revert_test.cairo test_with_except_revert" in result
    assert (
        "[PASS] tests/expect_revert_test.cairo test_call_not_existing_contract"
        in result
    )
    assert (
        "[PASS] tests/expect_revert_test.cairo test_call_not_existing_contract_err_message"
        in result
    )
    assert (
        "[FAIL] tests/expect_revert_test.cairo test_with_except_out_of_scope_revert_fail_expected"
        in result
    )
    assert (
        "[FAIL] tests/expect_revert_test.cairo test_call_not_existing_contract_fail_expected"
        in result
    )
    assert "[error_type] RANDOM_ERROR_NAME" in result
    assert (
        "[FAIL] tests/expect_revert_test.cairo test_error_was_not_raised_before_stopping_expect_revert_fail_expected"
        in result
    )
    assert "5 failed, 5 passed, 10 total" in result
    assert "Unknown location" not in result


def test_loading_cairo_path_from_config_file(protostar, my_private_libs_setup):
    (my_private_libs_dir,) = my_private_libs_setup

    with pytest.raises(CalledProcessError):
        protostar(["test", "tests"])

    with open("./protostar.toml", "a", encoding="utf-8") as protostar_toml:
        protostar_toml.write(
            f"""
["protostar.shared_command_configs"]
cairo_path = ["{str(my_private_libs_dir)}"]
"""
        )

    result = protostar(["test", "tests"])
    assert "/my_lib/utils.cairo" not in result
    assert "1 passed" in result


@pytest.mark.usefixtures("init")
def test_exit_code_if_any_test_failed(protostar, copy_fixture):
    copy_fixture("test_failed.cairo", "./tests")
    with pytest.raises(CalledProcessError):
        protostar(["test", "tests"])


@pytest.mark.usefixtures("init")
def test_broken_test_suite_in_collecting_phase(protostar, copy_fixture):
    copy_fixture("test_broken.cairo", "./tests")

    result: str = protostar(["--no-color", "test", "**/test_*"], ignore_exit_code=True)
    assert "1 broken, 1 passed" in result


@pytest.mark.usefixtures("init")
def test_disabling_hint_validation(protostar: ProtostarFixture, copy_fixture):
    copy_fixture("contract_with_invalid_hint.cairo", "./src")
    copy_fixture("contract_with_invalid_hint_test.cairo", "./tests")

    result_before = protostar(
        [
            "--no-color",
            "test",
            "tests/contract_with_invalid_hint_test.cairo",
        ],
        ignore_exit_code=True,
    )
    assert "Hint is not whitelisted" in result_before

    result_after = protostar(
        [
            "--no-color",
            "test",
            "tests/contract_with_invalid_hint_test.cairo",
            "--disable-hint-validation",
        ],
        ignore_exit_code=True,
    )
    assert "Hint is not whitelisted" not in result_after


@pytest.mark.usefixtures("init")
def test_exit_first_failed(protostar, copy_fixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_failed.cairo", "./tests")

    assert "skipped" in protostar(["test", "-x", "tests"], ignore_exit_code=True)
    assert "skipped" not in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_exit_first_broken(protostar, copy_fixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_broken.cairo", "./tests")

    assert "skipped" in protostar(["test", "-x", "tests"], ignore_exit_code=True)
    assert "skipped" not in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_print_passed(protostar, copy_fixture):
    copy_fixture("test_print_passed.cairo", "./tests")
    assert "captured stdout" in protostar(
        ["test", "--stdout-on-success", "tests"], ignore_exit_code=True
    )
    assert "captured stdout" not in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_print_failed(protostar, copy_fixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    assert "captured stdout" in protostar(
        ["test", "--stdout-on-success", "tests"], ignore_exit_code=True
    )
    assert "captured stdout" in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_print_both(protostar, copy_fixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(["test", "--stdout-on-success", "tests"], ignore_exit_code=True)

    assert result.count("captured stdout") == 2
    assert "Hello" in result
    assert "bee" in result

    result = protostar(["test", "tests"], ignore_exit_code=True)

    assert result.count("captured stdout") == 1
    assert "Hello" not in result
    assert "bee" in result


@pytest.mark.usefixtures("init")
def test_print_setup(protostar, copy_fixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(["test", "--stdout-on-success", "tests"], ignore_exit_code=True)

    assert "P_SETUP" in result
    assert "F_SETUP" in result
    assert "[test]:" in result
    assert "[setup]:" in result

    result = protostar(["test", "tests"], ignore_exit_code=True)

    assert "P_SETUP" not in result
    assert "F_SETUP" in result
    assert "[test]:" in result
    assert "[setup]:" in result


@pytest.mark.usefixtures("init")
def test_print_only_setup(protostar, copy_fixture):
    copy_fixture("test_print_only_setup.cairo", "./tests")

    result = protostar(["test", "--stdout-on-success", "tests"], ignore_exit_code=True)

    assert "O_SETUP" in result
    assert "[test]:" not in result
    assert "[setup]:" in result
