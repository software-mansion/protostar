from pathlib import Path

import pytest

from protostar.testing.test_results import TestCaseResult
from protostar.testing.testing_summary import TestingSummary
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_expect_events(protostar: ProtostarFixture):
    protostar.create_contracts({"emitter": CONTRACTS_PATH / "emitter.cairo"})

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "expect_events_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_expect_event_by_name",
            "test_expect_event_by_name_and_data",
            "test_expect_events_in_declared_order",
            "test_allow_checking_for_events_in_any_order",
        ],
        expected_failed_test_cases_names=[
            "test_fail_on_data_mismatch",
            "test_fail_when_no_events_were_emitted",
            "test_fail_message_about_first_not_found_event",
        ],
    )
    assert "[skip] name: EVENT_NAME" in protostar.format_test_result(
        find_test_case_result(testing_summary, "test_fail_on_data_mismatch")
    )


def find_test_case_result(testing_summary: TestingSummary, name: str) -> TestCaseResult:
    return [
        test_case_result
        for test_case_result in testing_summary.test_results
        if isinstance(test_case_result, TestCaseResult)
        and test_case_result.test_case_name == name
    ][0]
