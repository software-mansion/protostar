from pathlib import Path
import re
import pytest

from protostar.protostar_exception import ProtostarException
from tests.integration.conftest import (
    RunCairo0TestRunnerFixture,
)


@pytest.mark.skip
async def test_testing_output(run_cairo0_test_runner: RunCairo0TestRunnerFixture):
    await run_cairo0_test_runner(
        Path(__file__).parent / "example_profile_contract_test.cairo", profiling=True
    )
    assert False


async def test_failed_profile_multiple_tests(
    run_cairo0_test_runner: RunCairo0TestRunnerFixture,
):
    with pytest.raises(
        ProtostarException,
        match=re.escape(
            "Only one test case can be profiled at the time. Please specify path to a single test case."
        ),
    ):
        await run_cairo0_test_runner(
            Path(__file__).parent,
            profiling=True,
        )
