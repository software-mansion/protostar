from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
)


@pytest.mark.asyncio
async def test_testing_output(run_cairo_test_runner: RunCairoTestRunnerFixture):
    await run_cairo_test_runner(
        Path(__file__).parent / "testing_output_test.cairo"
    )
    assert False

