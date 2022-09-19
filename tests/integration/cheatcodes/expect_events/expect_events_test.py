from pathlib import Path
from typing import cast

import pytest

from protostar.testing.test_environment_exceptions import (
    ExpectedEventMissingException,
)
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_expect_events(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "expect_events_test.cairo",
        ignored_test_cases=["test_selector_to_name_mapping"],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_expect_event_by_name_and_data",
            "test_expect_event_by_name",
            "test_expect_event_emitted_by_external_contract",
            "test_expect_event_by_contract_address",
            "test_expect_events_in_declared_order",
            "test_allow_checking_for_events_in_any_order",
            "test_data_transformation",
            "test_data_transformation_in_contract_deployed_in_setup",
            "test_data_transformations_in_unit_testing_approach",
        ],
        expected_failed_test_cases_names=[
            "test_fail_on_data_mismatch",
            "test_fail_when_no_events_were_emitted",
            "test_fail_on_contract_address_mismatch",
            "test_fail_message_about_first_not_found_event",
        ],
    )


@pytest.mark.asyncio
async def test_event_selector_to_name_mapping(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent
        / "expect_events_test.cairo::test_selector_to_name_mapping"
    )

    ex = cast(ExpectedEventMissingException, testing_summary.failed[0].exception)
    str_ex = str(ex)
    assert '"name": "foobar"' in str_ex
    assert '"name": "balance_increased"' in str_ex
