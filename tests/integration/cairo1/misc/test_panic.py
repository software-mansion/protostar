from pathlib import Path

import pytest

from protostar.starknet import SimpleReportedException
from protostar.testing.test_results import FailedTestCaseResult
from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar_project", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        yield protostar_project


async def test_panic(protostar_project: ProtostarProjectFixture, datadir: Path):
    testing_summary = await protostar_project.protostar.test(
        datadir / "panic_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_failed_test_cases_names=[
            "test_panic_when_felt252_not_short_str",
            "test_panic_with_felt252_max_val",
        ],
    )

    expected_outputs = {
        "test_panic_when_felt252_not_short_str": [
            "Test failed with data:",
            "[1234] (integer representation)",
            "[None] (short-string representation)",
        ],
        "test_panic_with_felt252_max_val": [
            "Test failed with data:",
            "[3618502788666131213697322783095070105623107215331596699973092056135872020480] (integer representation)",
            "[None] (short-string representation)",
        ],
    }

    mapping_item = testing_summary.test_suites_mapping.get(datadir / "panic_test.cairo")
    assert mapping_item is not None

    for item in mapping_item:
        assert isinstance(item, FailedTestCaseResult)
        expected_outputs_list = expected_outputs[item.test_case_name]
        for expected_output in expected_outputs_list:
            assert isinstance(item.exception, SimpleReportedException)
            assert expected_output in item.exception.message
