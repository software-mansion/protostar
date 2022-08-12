from pathlib import Path
from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_assume_and_reject_cheatcodes(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "assume_and_reject_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_passed_assume"],
        expected_failed_test_cases_names=[
            "test_assume_not_fuzz",
            "test_reject_not_fuzz",
        ],
    )


async def test_assume_and_reject_cheatcodes_together(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "assume_and_reject_together_test.cairo", seed=42
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=["test_failed_assume_and_reject_together"],
    )

    metadata = testing_summary.failed[0].exception.metadata
    assert metadata
    assert isinstance(metadata[0], FuzzInputExceptionMetadata)
    assert {"a": -1, "b": -2} == metadata[0].inputs
