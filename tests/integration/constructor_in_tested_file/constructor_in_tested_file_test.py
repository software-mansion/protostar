# pylint: disable=protected-access
from pathlib import Path

import pytest

from tests.integration.conftest import RunCairoTestRunnerFixture


@pytest.fixture(name="pretty_printed_error_message_substring")
def pretty_printed_error_message_substring_fixture() -> str:
    return "constructor expecting arguments"


@pytest.mark.asyncio
async def test_should_pretty_print_constructor_error(
    pretty_printed_error_message_substring: str,
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_contract_test.cairo"
    )

    assert len(testing_summary.broken) == 1
    assert pretty_printed_error_message_substring in str(
        testing_summary.broken[0].exception
    )


@pytest.mark.asyncio
async def test_should_not_break_test_suite(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_contract_integration_test.cairo",
    )

    assert len(testing_summary.broken) == 0


@pytest.mark.asyncio
async def test_not_pretty_printing_the_constructor_error(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
    pretty_printed_error_message_substring: str,
):

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "error_from_deploy_syscall_test.cairo"
    )

    assert len(testing_summary.failed) == 1
    assert pretty_printed_error_message_substring not in str(
        testing_summary.failed[0].exception
    )
