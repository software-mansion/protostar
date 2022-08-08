# pylint: disable=invalid-name
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Set, Union

import pytest
from pytest_mock import MockerFixture
from typing_extensions import Protocol

from protostar.commands.test.test_collector_result_logger import (
    TestCollectorResultLogger,
)
from protostar.commands.test.test_command import TestCommand
from protostar.commands.test.test_result_formatter import TestResultFormatter
from protostar.commands.test.testing_summary import TestingSummary
from protostar.utils.log_color_provider import LogColorProvider
from tests.conftest import run_devnet


@dataclass
class CairoTestCases:
    passed: Set[str]
    failed: Set[str]
    broken: Union[int, Set[str]]

    def __repr__(self) -> str:
        passed = "[Passed]\n" + "\n".join(sorted(self.passed))
        failed = "[Failed]\n" + "\n".join(sorted(self.failed))

        if isinstance(self.broken, int):
            broken = f"Broken count: {self.broken}"
        else:
            broken = "[Broken]\n" + "\n".join(sorted(self.broken))

        return "\n".join([passed, failed, broken])


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: List[str],
    expected_failed_test_cases_names: List[str],
    expected_broken_test_cases_names: Optional[List[str]] = None,
):
    passed_test_cases_names = set(
        passed_test_case.test_case_name for passed_test_case in testing_summary.passed
    )
    failed_test_cases_names = set(
        failed_test_case.test_case_name for failed_test_case in testing_summary.failed
    )

    if expected_broken_test_cases_names is None:
        actual_broken = len(testing_summary.broken)
    else:
        actual_broken = set()
        for broken_test_case in testing_summary.broken:
            for test_case_name in broken_test_case.test_case_names:
                actual_broken.add(test_case_name)

    actual = CairoTestCases(
        passed=passed_test_cases_names,
        failed=failed_test_cases_names,
        broken=actual_broken,
    )

    if expected_broken_test_cases_names is None:
        expected_broken = 0
    else:
        expected_broken = set(expected_broken_test_cases_names)

    expected = CairoTestCases(
        passed=set(expected_passed_test_cases_names),
        failed=set(expected_failed_test_cases_names),
        broken=expected_broken,
    )

    assert actual == expected


@pytest.fixture(name="devnet_gateway_url", scope="module")
def devnet_gateway_url_fixture(devnet_port: int):
    proc = run_devnet(["poetry", "run", "starknet-devnet"], devnet_port)
    yield f"http://localhost:{devnet_port}"
    proc.kill()


class RunCairoTestRunnerFixture(Protocol):
    async def __call__(
        self,
        path: Path,
        seed: Optional[int] = None,
        fuzz_max_examples=100,
    ) -> TestingSummary:
        ...


@pytest.fixture(name="run_cairo_test_runner")
def run_cairo_test_runner_fixture(mocker: MockerFixture) -> RunCairoTestRunnerFixture:
    async def run_cairo_test_runner(
        path: Path,
        seed: Optional[int] = None,
        fuzz_max_examples=100,
    ) -> TestingSummary:
        log_color_provider = LogColorProvider()
        log_color_provider.is_ci_mode = False
        test_result_formatter = TestResultFormatter(log_color_provider)
        return await TestCommand(
            project_root_path=Path(),
            protostar_directory=mocker.MagicMock(),
            project_cairo_path_builder=mocker.MagicMock(),
            test_collector_result_logger=TestCollectorResultLogger(
                logger=getLogger(),
                test_result_formatter=test_result_formatter,
            ),
            test_result_formatter=test_result_formatter,
        ).test(targets=[str(path)], seed=seed, fuzz_max_examples=fuzz_max_examples)

    return run_cairo_test_runner
