from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from protostar.testing.test_results import PassedTestCaseResult


@pytest.fixture(name="protostar_project", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        yield protostar_project


async def test_print(protostar_project: ProtostarProjectFixture, datadir: Path):
    testing_summary = await protostar_project.protostar.test(
        datadir / "print_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_print_basic"],
    )

    expected_outputs = {
        "test_print_basic": [
            "original value: [448378203247] converted to a string: [hello]",
            "original value: [1953658213] converted to a string: [true]",
            "original value: [439721161573] converted to a string: [false]",
            "original value: [1953658213] converted to a string: [true]",
            "original value: [1986358889] converted to a string: [veni]",
            "original value: [1986618473] converted to a string: [vidi]",
            "original value: [1986618217] converted to a string: [vici]",
            "original value: [128]",
            "original value: [3618502788666131213697322783095070105623107215331596699973092056135872020480]",
        ],
    }

    mapping_item = testing_summary.test_suites_mapping.get(datadir / "print_test.cairo")
    assert mapping_item is not None

    for item in mapping_item:
        assert isinstance(item, PassedTestCaseResult)
        expected_outputs_list = expected_outputs[item.test_case_name]
        for expected_output in expected_outputs_list:
            assert expected_output in item.captured_stdout["test"]
