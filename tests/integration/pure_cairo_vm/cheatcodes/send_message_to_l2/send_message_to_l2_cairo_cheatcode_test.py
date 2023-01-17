import asyncio
from pathlib import Path

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture


def test_l1_to_l2_message_cheatcode(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
    create_protostar_project: CreateProtostarProjectFixture,
):
    with create_protostar_project() as protostar:
        contracts_sources_path = Path(__file__).parent
        protostar.create_files(
            {
                "tests/test_main.cairo": contracts_sources_path
                / "simple_l1_handler_test.cairo",
                "src/main.cairo": contracts_sources_path
                / "external_contract_with_l1_handler.cairo",
            }
        )
        protostar.build_sync()

        testing_summary = asyncio.run(run_cairo_test_runner(Path(".")))

        assert_cairo_test_cases(
            testing_summary,
            expected_passed_test_cases_names=[
                "test_happy_case",
            ],
        )
