# pylint: disable=invalid-name
from pathlib import Path
from typing import List

import pytest
from pytest_mock import MockerFixture

from protostar.commands.test.test_command import TestCommand
from protostar.commands.test.testing_summary import TestingSummary
from tests.conftest import run_devnet


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: List[str],
    expected_failed_test_cases_names: List[str],
):

    passed_test_cases_names = [
        passed_test_case.test_case_name for passed_test_case in testing_summary.passed
    ]
    failed_test_cases_names = [
        failed_test_case.test_case_name for failed_test_case in testing_summary.failed
    ]
    assert set(expected_passed_test_cases_names) == set(passed_test_cases_names)
    assert set(expected_failed_test_cases_names) == set(failed_test_cases_names)
    assert len(testing_summary.broken) == 0


@pytest.fixture(name="devnet_gateway_url", scope="module")
def devnet_gateway_url_fixture(devnet_port: int):
    proc = run_devnet(["poetry", "run", "starknet-devnet"], devnet_port)
    yield f"http://localhost:{devnet_port}"
    proc.kill()



async def run_cairo_test_runner(mocker: MockerFixture, path: Path) -> TestingSummary:
    return await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[str(path)])
