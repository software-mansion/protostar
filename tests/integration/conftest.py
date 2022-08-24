# pylint: disable=invalid-name
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Set, Union, cast

import pytest
from pytest import TempPathFactory
from pytest_mock import MockerFixture
from typing_extensions import Protocol

from protostar.commands.test.test_command import TestCommand
from protostar.commands.test.testing_summary import TestingSummary
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.utils.log_color_provider import LogColorProvider
from tests.conftest import run_devnet
from tests.integration.protostar_fixture import (
    ProtostarFixture,
    build_protostar_fixture,
)


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


@pytest.fixture(name="devnet_gateway_url", scope="session")
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
        disable_hint_validation=False,
        cairo_path: Optional[List[Path]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:
        ...


@pytest.fixture(name="log_color_provider")
def log_color_provider_fixture() -> LogColorProvider:
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    return log_color_provider


@pytest.fixture(name="run_cairo_test_runner")
def run_cairo_test_runner_fixture(
    mocker: MockerFixture, log_color_provider: LogColorProvider
) -> RunCairoTestRunnerFixture:
    async def run_cairo_test_runner(
        path: Path,
        seed: Optional[int] = None,
        fuzz_max_examples=100,
        disable_hint_validation=False,
        cairo_path: Optional[List[Path]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:

        protostar_directory_mock = mocker.MagicMock()
        protostar_directory_mock.protostar_test_only_cairo_packages_path = Path()

        project_cairo_path_builder = cast(ProjectCairoPathBuilder, mocker.MagicMock())
        project_cairo_path_builder.build_project_cairo_path_list = (
            lambda relative_cairo_path_list: relative_cairo_path_list
        )

        ignored_targets: Optional[List[str]] = None
        if ignored_test_cases:
            ignored_targets = [
                f"{str(path)}::{ignored_test_case}"
                for ignored_test_case in ignored_test_cases
            ]

        return await TestCommand(
            project_root_path=Path(),
            protostar_directory=protostar_directory_mock,
            project_cairo_path_builder=project_cairo_path_builder,
            logger=getLogger(),
            log_color_provider=log_color_provider,
        ).test(
            targets=[str(path)],
            ignored_targets=ignored_targets,
            seed=seed,
            fuzz_max_examples=fuzz_max_examples,
            disable_hint_validation=disable_hint_validation,
            cairo_path=cairo_path or [],
        )

    return run_cairo_test_runner


@pytest.fixture(name="protostar_project_root_path", scope="module")
def protostar_project_root_path_fixture(tmp_path_factory: TempPathFactory) -> Path:
    tmp_path = tmp_path_factory.mktemp("data")
    return tmp_path / "tmp_project"


@pytest.fixture(name="protostar", scope="module")
def protostar_fixture(
    session_mocker: MockerFixture,
    protostar_project_root_path: Path,
    signer,
) -> ProtostarFixture:
    return build_protostar_fixture(
        mocker=session_mocker,
        project_root_path=protostar_project_root_path,
        signer=signer,
    )
