from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
)


@pytest.mark.asyncio
# @pytest.mark.skip
async def test_testing_output(run_cairo_test_runner: RunCairoTestRunnerFixture):
    await run_cairo_test_runner(
        Path(__file__).parent / "example_profile_contract_test.cairo"
    )
    assert False
