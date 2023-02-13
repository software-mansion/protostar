from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    assert_cairo_test_cases,
    CreateProtostarProjectFixture,
)
from tests.integration.pure_cairo_vm.conftest import (
    CONTRACTS_PATH,
)


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_pure_cairo_testing(protostar: ProtostarFixture):
    protostar.create_files(
        {
            "src/library.cairo": Path(__file__).parent / "library.cairo",
        }
    )
    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "pure_cairo_test.cairo",
        cairo_test_runner=True,
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


async def test_pure_cairo_broken_test(protostar: ProtostarFixture):
    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "pure_cairo_broken_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[],
        expected_broken_test_cases_names=["test_broken_case"],
    )


async def test_setup_suite(protostar: ProtostarFixture):
    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "suite_with_setup_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_setup_executed"],
    )


async def test_setup_suite_with_satellite_contract(
    protostar: ProtostarFixture,
):
    protostar.create_files(
        {
            "src/main.cairo": CONTRACTS_PATH / "basic_contract.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "suite_with_setup_and_cheatcodes_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_setup_with_deployment",
            "test_suites_with_setups_dont_leak_state",
        ],
    )


async def test_setup_case_with_satellite_contract(
    protostar: ProtostarFixture,
):
    protostar.create_files(
        {
            "src/main.cairo": CONTRACTS_PATH / "basic_contract.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "suite_with_setup_case_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_a", "test_b_doesnt_leak_from_a_setup"],
    )


async def test_syscall_deployment_abi_storing(
    protostar: ProtostarFixture,
):
    protostar.create_contracts(
        {
            "block_number_contract": CONTRACTS_PATH / "block_number_contract.cairo",
            "deployer": CONTRACTS_PATH / "deployer.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "cheatable_syscall_handler_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_syscall_deployment_abi_storing"],
    )
