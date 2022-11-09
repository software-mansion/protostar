import shutil
from os import listdir
from pathlib import Path
from textwrap import dedent

import pytest

from tests.e2e.conftest import CopyFixture, MyPrivateLibsSetupFixture, ProtostarFixture


@pytest.mark.usefixtures("init")
def test_basic_contract(protostar: ProtostarFixture):
    result = protostar(["test", "tests"])
    assert "1 passed" in result
    assert "Seed:" in result


@pytest.mark.usefixtures("init")
def test_safe_collecting(protostar: ProtostarFixture):
    result = protostar(["test", "--safe-collecting"])
    assert "1 passed" in result


@pytest.mark.usefixtures("init")
def test_basic_contract_profile(protostar: ProtostarFixture):
    result = protostar(
        ["test", "--profiling", "tests/test_main.cairo::test_increase_balance"]
    )
    assert "1 passed" in result
    assert "profile.pb.gz" in listdir(".")


@pytest.mark.usefixtures("init")
def test_profile_fuzz(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("fuzz_test.cairo", "./tests")
    result = protostar(
        ["test", "--profiling", "tests/fuzz_test.cairo"], ignore_exit_code=True
    )
    assert "Fuzz tests cannot be profiled" in result
    assert not Path("profile.pb.gz").exists()


@pytest.mark.usefixtures("init")
def test_complex(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")

    result = protostar(["test", "tests"])

    assert "Collected 2 suites, and 4 test cases" in result
    assert "4 passed" in result


@pytest.mark.usefixtures("init")
def test_expect_revert(protostar_repo_root: Path, protostar: ProtostarFixture):
    shutil.copy(
        protostar_repo_root
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
    assert "1 broken, 5 failed, 5 passed, 11 total" in result
    assert "Unknown location" not in result


def test_loading_cairo_path_from_config_file(
    protostar: ProtostarFixture, my_private_libs_setup: MyPrivateLibsSetupFixture
):
    (my_private_libs_dir,) = my_private_libs_setup

    protostar(["test", "tests"], expect_exit_code=1)

    Path("protostar.toml").write_text(
        dedent(
            f"""
            [project]
            protostar-version="0.0.0"
            cairo-path = ["{str(my_private_libs_dir)}"]

            [contracts]
            main = ["src/main.cairo"]
        """
        ),
        encoding="utf-8",
    )

    result = protostar(["test", "tests"])
    assert "/my_lib/utils.cairo" not in result
    assert "1 passed" in result


@pytest.mark.usefixtures("init")
def test_exit_code_if_any_test_failed(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("test_failed.cairo", "./tests")
    protostar(["test", "tests"], expect_exit_code=1)


@pytest.mark.usefixtures("init")
def test_broken_test_suite_in_collecting_phase(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("test_broken.cairo", "./tests")

    result: str = protostar(["--no-color", "test", "**/test_*"], ignore_exit_code=True)
    assert "1 broken, 1 passed" in result


@pytest.mark.usefixtures("init")
def test_disabling_hint_validation(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
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
def test_exit_first_failed(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_failed.cairo", "./tests")

    assert "skipped" in protostar(["test", "-x", "tests"], ignore_exit_code=True)
    assert "skipped" not in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_exit_first_broken(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_broken.cairo", "./tests")

    assert "skipped" in protostar(["test", "-x", "tests"], ignore_exit_code=True)
    assert "skipped" not in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_print_passed(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_passed.cairo", "./tests")
    assert "captured stdout" in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_print_failed(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    assert "captured stdout" in protostar(["test", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init")
def test_print_both(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(["test", "tests"], ignore_exit_code=True)

    assert result.count("captured stdout") == 2
    assert "Hello" in result
    assert "bee" in result


@pytest.mark.usefixtures("init")
def test_print_setup(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(["test", "tests"], ignore_exit_code=True)

    assert "P __setup__" in result
    assert "F __setup__" in result
    assert "P setup_should_pass" in result
    assert "F setup_should_fail" in result
    assert "[test]:" in result
    assert "[setup]:" in result
    assert "[setup case]:" in result


@pytest.mark.usefixtures("init")
def test_print_only_setup(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_only_setup.cairo", "./tests")

    result = protostar(["test", "tests"], ignore_exit_code=True)

    assert "O __setup__" in result
    assert "[test]:" not in result
    assert "[setup]:" in result


@pytest.mark.usefixtures("init")
def test_report_slowest(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(
        ["test", "tests", "--report-slowest-tests", "999999"], ignore_exit_code=True
    )

    assert "Slowest test cases" in result


@pytest.mark.usefixtures("init")
def test_does_collect_in_cwd_by_default(protostar: ProtostarFixture):
    result = protostar(["test"])
    assert "Collected 1 suite, and 2 test cases" in result


@pytest.mark.usefixtures("init")
def test_skipping(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_skip.cairo", "./tests")
    result = protostar(["test", "tests"])
    assert "SKIP" in result
    assert "REASON" in result


@pytest.mark.usefixtures("init")
def test_max_steps(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_step.cairo", "./tests")

    result = protostar(["test", "tests", "--max-steps", "10"], ignore_exit_code=True)
    assert "FAIL" in result
    assert "OUT_OF_RESOURCES" in result

    result = protostar(["test", "tests", "--max-steps", "-1"])
    assert "PASS" in result

    result = protostar(["test", "tests", "--max-steps", "1000"])
    assert "PASS" in result
