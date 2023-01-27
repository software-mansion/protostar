from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH

TEST_PATH = Path(__file__).parent / "expect_events_test.cairo"


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_expect_events(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "emitter": CONTRACTS_PATH / "emitter.cairo",
        }
    )
    testing_summary = await protostar.run_test_runner(
        TEST_PATH,
        cairo_test_runner=True,
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
            "test_fail_selector_to_name_mapping",
        ],
    )
