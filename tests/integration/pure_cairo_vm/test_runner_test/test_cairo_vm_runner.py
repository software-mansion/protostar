from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    assert_cairo_test_cases,
    CreateProtostarProjectFixture,
)
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture

CONTRACTS_PATH = Path(__file__).parent.parent / "contracts"


async def test_pure_cairo_testing(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "pure_cairo_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_simple_passing",
            "test_simple_import_function",
        ],
        expected_failed_test_cases_names=["test_simple_failing"],
        expected_broken_test_cases_names=[],
    )


async def test_pure_cairo_broken_test(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "pure_cairo_broken_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[],
        expected_broken_test_cases_names=["test_broken_case"],
    )


async def test_setup_suite(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "suite_with_setup_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_setup_executed"],
    )


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_setup_suite_with_satellite_contract(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
    protostar: ProtostarFixture,
):
    protostar.create_files(
        {
            "src/main.cairo": CONTRACTS_PATH / "basic_contract.cairo",
        }
    )

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "suite_with_setup_and_cheatcodes_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_setup_with_deployment",
            "test_suites_with_setups_dont_leak_state",
        ],
    )
