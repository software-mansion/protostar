from pathlib import Path

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


async def test_disabling_hint_validation(mocker):
    async def run_test(disable_hint_validation: bool):
        return await TestCommand(
            project_root_path=Path(),
            project_cairo_path_builder=mocker.MagicMock(),
            protostar_directory=mocker.MagicMock(),
            test_collector_result_logger=mocker.MagicMock(),
            test_result_formatter=mocker.MagicMock(),
        ).test(
            targets=[f"{Path(__file__).parent}/disabling_hint_validation_test.cairo"],
            disable_hint_validation=disable_hint_validation,
        )

    testing_summary_before = await run_test(disable_hint_validation=False)
    assert_cairo_test_cases(
        testing_summary_before,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=["test_invalid_hint_in_deployed_contract"],
    )
    assert "Hint is not whitelisted" in str(testing_summary_before.failed[0].exception)

    testing_summary_after = await run_test(disable_hint_validation=True)
    assert_cairo_test_cases(
        testing_summary_after,
        expected_passed_test_cases_names=["test_invalid_hint_in_deployed_contract"],
        expected_failed_test_cases_names=[],
    )
