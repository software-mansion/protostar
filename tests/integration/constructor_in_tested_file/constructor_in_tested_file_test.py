from pathlib import Path

from tests.integration.conftest import RunCairoTestRunnerFixture


async def test_should_accept_case_with_constructor(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_contract_test.cairo"
    )

    assert len(testing_summary.broken_suites) == 0
