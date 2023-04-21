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
    protostar_project.create_contracts_cairo1(
        {
            "simple": datadir / "simple",
        }
    )
    testing_summary = await protostar_project.protostar.run_test_runner(
        datadir / "basic_print_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_print_basic", "test_print_in_contract"],
    )

    expected_outputs = {
        "test_print_in_contract": [
            "original value: [123]",
            "original value: [3]",
            "original value: [24]",
            "original value: [72]",
        ],
        "test_print_basic": [
            "original value: [448378203247] converted to a string: [hello]",
            "original value: [439721161573] converted to a string: [false]",
            "original value: [1953658213] converted to a string: [true]",
        ],
    }

    mapping_item = testing_summary.test_suites_mapping.get(
        datadir / "basic_print_test.cairo"
    )
    assert mapping_item is not None

    for item in mapping_item:
        assert isinstance(item, PassedTestCaseResult)
        expected_outputs_list = expected_outputs[item.test_case_name]
        for expected_output in expected_outputs_list:
            assert expected_output in item.captured_stdout["test"]
