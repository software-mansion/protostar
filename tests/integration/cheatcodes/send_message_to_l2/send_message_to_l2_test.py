import asyncio
from pathlib import Path

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    RunCairo0TestRunnerFixture,
    assert_cairo_test_cases,
)


def test_l1_to_l2_message_cheatcode(
    run_cairo0_test_runner: RunCairo0TestRunnerFixture,
    create_protostar_project: CreateProtostarProjectFixture,
):
    with create_protostar_project() as protostar_project:
        contracts_sources_path = Path(__file__).parent

        protostar_project.create_files(
            {
                "tests/test_main.cairo": contracts_sources_path
                / "simple_l1_handler_test.cairo",
                "tests/test_data_transformer.cairo": contracts_sources_path
                / "data_transformer_l1_handler_test.cairo",
                "tests/test_address_verification.cairo": contracts_sources_path
                / "address_verification_l1_handler_test.cairo",
                "src/main.cairo": contracts_sources_path
                / "external_contract_with_l1_handler.cairo",
            }
        )
        protostar_project.protostar.build_cairo0_sync()

        testing_summary = asyncio.run(
            run_cairo0_test_runner(
                Path("."),
            )
        )

        assert_cairo_test_cases(
            testing_summary,
            expected_passed_test_cases_names=[
                "test_existing_self_l1_handle_call",
                "test_existing_self_l1_handle_call_w_transformer",
                "test_existing_self_l1_handle_call_no_calldata",
                "test_existing_self_l1_handle_call_custom_l1_sender_address",
                "test_existing_external_contract_l1_handle_call",
                "test_sending_events_from_test_case_and_l1_handler",
            ],
            expected_broken_test_cases_names=["test_non_existing_self_l1_handle_call"],
        )
