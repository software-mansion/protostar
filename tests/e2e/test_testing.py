import json
import os
import shutil

# from os import listdir
from pathlib import Path
from textwrap import dedent

import pytest

from tests.e2e.conftest import CopyFixture, MyPrivateLibsSetupFixture, ProtostarFixture


@pytest.mark.usefixtures("init_cairo0")
def test_basic_contract(protostar: ProtostarFixture):
    result = protostar(["test-cairo0", "tests"])
    assert "1 passed" in result
    assert "Seed:" in result


@pytest.mark.usefixtures("init_cairo0")
def test_safe_collecting(protostar: ProtostarFixture):
    result = protostar(["test-cairo0", "--safe-collecting"])
    assert "1 passed" in result


@pytest.mark.usefixtures("init_cairo0")
def test_complex(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")

    result = protostar(["test-cairo0", "tests"])

    assert "Collected 2 suites, and 4 test cases" in result
    assert "4 passed" in result


@pytest.mark.usefixtures("init_cairo0")
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
        ["--no-color", "test-cairo0", "tests/expect_revert_test.cairo"],
        ignore_exit_code=True,
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

    protostar(["test-cairo0", "tests"], expect_exit_code=1)

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

    result = protostar(["test-cairo0", "tests"])
    assert "/my_lib/utils.cairo" not in result
    assert "1 passed" in result


@pytest.mark.usefixtures("init_cairo0")
def test_exit_code_if_any_test_failed(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("test_failed.cairo", "./tests")
    protostar(["test-cairo0", "tests"], expect_exit_code=1)


@pytest.mark.usefixtures("init_cairo0")
def test_broken_test_suite_in_collecting_phase(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("test_broken.cairo", "./tests")

    result: str = protostar(
        ["--no-color", "test-cairo0", "**/test_*"], ignore_exit_code=True
    )
    assert "1 broken, 1 passed" in result


@pytest.mark.usefixtures("init_cairo0")
def test_disabling_hint_validation(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("contract_with_invalid_hint.cairo", "./src")
    copy_fixture("contract_with_invalid_hint_test.cairo", "./tests")

    result_before = protostar(
        [
            "--no-color",
            "test-cairo0",
            "tests/contract_with_invalid_hint_test.cairo",
        ],
        ignore_exit_code=True,
    )
    assert "Hint is not whitelisted" in result_before

    result_after = protostar(
        [
            "--no-color",
            "test-cairo0",
            "tests/contract_with_invalid_hint_test.cairo",
            "--disable-hint-validation",
        ],
        ignore_exit_code=True,
    )
    assert "Hint is not whitelisted" not in result_after


@pytest.mark.usefixtures("init_cairo0")
def test_exit_first_failed(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_failed.cairo", "./tests")

    assert "skipped" in protostar(["test-cairo0", "-x", "tests"], ignore_exit_code=True)
    assert "skipped" not in protostar(["test-cairo0", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init_cairo0")
def test_exit_first_broken(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_broken.cairo", "./tests")

    assert "skipped" in protostar(["test-cairo0", "-x", "tests"], ignore_exit_code=True)
    assert "skipped" not in protostar(["test-cairo0", "tests"], ignore_exit_code=True)


@pytest.mark.usefixtures("init_cairo0")
def test_print_passed(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_passed.cairo", "./tests")
    assert "captured stdout" in protostar(
        ["test-cairo0", "tests"], ignore_exit_code=True
    )


@pytest.mark.usefixtures("init_cairo0")
def test_print_failed(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    assert "captured stdout" in protostar(
        ["test-cairo0", "tests"], ignore_exit_code=True
    )


@pytest.mark.usefixtures("init_cairo0")
def test_print_both(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(["test-cairo0", "tests"], ignore_exit_code=True)

    assert result.count("captured stdout") == 2
    assert "Hello" in result
    assert "bee" in result


@pytest.mark.usefixtures("init_cairo0")
def test_print_setup(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(["test-cairo0", "tests"], ignore_exit_code=True)

    assert "P __setup__" in result
    assert "F __setup__" in result
    assert "P setup_should_pass" in result
    assert "F setup_should_fail" in result
    assert "[test]:" in result
    assert "[setup]:" in result
    assert "[setup case]:" in result


@pytest.mark.usefixtures("init_cairo0")
def test_print_only_setup(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_print_only_setup.cairo", "./tests")

    result = protostar(["test-cairo0", "tests"], ignore_exit_code=True)

    assert "O __setup__" in result
    assert "[test]:" not in result
    assert "[setup]:" in result


@pytest.mark.usefixtures("init_cairo0")
def test_report_slowest(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("basic.cairo", "./src")
    copy_fixture("proxy_contract.cairo", "./src")
    copy_fixture("test_proxy.cairo", "./tests")
    copy_fixture("test_failed.cairo", "./tests")
    copy_fixture("test_print_passed.cairo", "./tests")

    result = protostar(
        ["test-cairo0", "tests", "--report-slowest-tests", "999999"],
        ignore_exit_code=True,
    )

    assert "Slowest test cases" in result


@pytest.mark.usefixtures("init_cairo0")
def test_does_collect_in_cwd_by_default(protostar: ProtostarFixture):
    result = protostar(["test-cairo0"])
    assert "Collected 1 suite, and 2 test cases" in result


@pytest.mark.usefixtures("init_cairo0")
def test_skipping(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    copy_fixture("test_skip.cairo", "./tests")
    result = protostar(["test-cairo0", "tests"])
    assert "SKIP" in result
    assert "REASON" in result


@pytest.mark.usefixtures("init_cairo0")
def test_structured_output_passed_failed(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("test_failed.cairo", "./tests")
    copy_fixture("test_passed.cairo", "./tests")
    copy_fixture("test_skip.cairo", "./tests")
    result = protostar(
        [
            "test-cairo0",
            "tests/test_failed.cairo",
            "tests/test_passed.cairo",
            "tests/test_skip.cairo",
            "--json",
        ],
        expect_exit_code=1,
    )

    ndjson_result = []
    for item in result.split(os.linesep):
        try:
            ndjson_result.append(json.loads(item))
        except json.decoder.JSONDecodeError:
            pass

    for item in ndjson_result:
        message_type = item.get("message_type")
        assert message_type in [
            "test_collector_result",
            "testing_summary",
            "test_case_result",
        ]
        if message_type == "test_case_result":
            assert item["test_type"] in [
                "failed_test_case",
                "passed_test_case",
                "skipped_test_case",
            ]
        if message_type == "testing_summary":
            assert item["test_suite_counts"]["total"] == 3
            assert item["test_suite_counts"]["failed"] == 1
            assert item["test_suite_counts"]["passed"] == 2

            assert item["test_case_counts"]["total"] == 3
            assert item["test_case_counts"]["failed"] == 1
            assert item["test_case_counts"]["passed"] == 1
            assert item["test_case_counts"]["skipped"] == 1


@pytest.mark.usefixtures("init_cairo0")
def test_structured_output_broken(
    protostar: ProtostarFixture, copy_fixture: CopyFixture
):
    copy_fixture("test_broken.cairo", "./tests")
    result = protostar(
        ["test-cairo0", "tests/test_broken.cairo", "--json"], expect_exit_code=1
    )

    ndjson_result = []
    for item in result.split(os.linesep):
        try:
            ndjson_result.append(json.loads(item))
        except json.decoder.JSONDecodeError:
            pass

    assert len(ndjson_result) == 1
    assert ndjson_result[0]["message_type"] == "test_collector_result"
    assert ndjson_result[0]["broken_test_suites_count"] == 1
