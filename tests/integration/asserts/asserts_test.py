from pathlib import Path

from tests.integration.conftest import (
    RunTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_asserts(run_test_runner: RunTestRunnerFixture):
    testing_summary = await run_test_runner(
        Path(__file__).parent / "asserts_test.cairo",
        cairo_path=[Path() / "protostar_cairo"],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_assert_eq",
            "test_assert_not_eq",
            "test_assert_signed_lt",
            "test_assert_unsigned_lt",
            "test_assert_signed_le",
            "test_assert_unsigned_le",
            "test_assert_signed_gt",
            "test_assert_unsigned_gt",
            "test_assert_signed_ge",
            "test_assert_unsigned_ge",
        ],
        expected_failed_test_cases_names=[],
    )
