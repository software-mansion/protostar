# pylint: disable=invalid-name
from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.mark.asyncio
async def test_asserts(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "asserts_test.cairo", cairo_path=[Path() / "cairo"]
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
