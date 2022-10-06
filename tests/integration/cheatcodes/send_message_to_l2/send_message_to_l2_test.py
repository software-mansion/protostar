import asyncio
from pathlib import Path

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases, CreateProtostarProjectFixture,
)


def test_l1_to_l2_message_cheatcode(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
    create_protostar_project: CreateProtostarProjectFixture,
):
    with create_protostar_project() as protostar:

        def read_contract_file(file_name: str) -> str:
            return (Path(__file__).parent / file_name).read_text("utf-8")

        protostar.create_files(
            {
                "tests/test_main.cairo": read_contract_file("simple_l1_handler_test.cairo"),
                "src/main.cairo": read_contract_file("external_contract_with_l1_handler.cairo")
            }
        )
        protostar.build_sync()

        testing_summary = asyncio.run(run_cairo_test_runner('.'))

        assert_cairo_test_cases(
            testing_summary,
            expected_passed_test_cases_names=[
                "test_existing_self_l1_handle_call",
                "test_existing_self_l1_handle_call_w_transformer",
                "test_existing_self_l1_handle_call_no_calldata",
                "test_existing_self_l1_handle_call_custom_l1_sender_address",
                "test_existing_external_contract_l1_handle_call",
            ],
            expected_broken_test_cases_names=["test_non_existing_self_l1_handle_call"],
        )
