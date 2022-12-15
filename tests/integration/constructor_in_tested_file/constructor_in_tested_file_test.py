from pathlib import Path

from tests.integration.conftest import RunTestRunnerFixture


async def test_should_accept_case_with_constructor(
    run_test_runner: RunTestRunnerFixture,
):
    testing_summary = await run_test_runner(
        Path(__file__).parent / "basic_contract_test.cairo"
    )

    assert len(testing_summary.broken_suites) == 0
