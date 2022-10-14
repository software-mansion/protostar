# pylint: disable=invalid-name
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Callable, ContextManager, List, Optional, Set, Tuple, cast

import pytest
from pytest import TempPathFactory
from pytest_mock import MockerFixture
from starkware.starknet.public.abi import AbiType
from typing_extensions import Protocol

from protostar.commands.test.test_command import TestCommand
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.io.log_color_provider import LogColorProvider
from protostar.testing import TestingSummary
from tests.conftest import run_devnet
from tests.integration.protostar_fixture import (
    ProtostarFixture,
    build_protostar_fixture,
)


@dataclass
class CairoTestCases:
    passed: Set[str]
    failed: Set[str]
    broken: Set[str]
    skipped: Set[str]

    def __repr__(self) -> str:
        passed = "[Passed]\n" + "\n".join(sorted(self.passed))
        failed = "[Failed]\n" + "\n".join(sorted(self.failed))
        broken = "[Broken]\n" + "\n".join(sorted(self.broken))
        skipped = "[Skipped]\n" + "\n".join(sorted(self.skipped))

        return "\n".join([passed, failed, broken, skipped])


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: Optional[List[str]] = None,
    expected_failed_test_cases_names: Optional[List[str]] = None,
    expected_broken_test_cases_names: Optional[List[str]] = None,
    expected_skipped_test_cases_names: Optional[List[str]] = None,  # Explicitly skipped
):
    expected_passed_test_cases_names = expected_passed_test_cases_names or []
    expected_failed_test_cases_names = expected_failed_test_cases_names or []
    expected_broken_test_cases_names = expected_broken_test_cases_names or []
    expected_skipped_test_cases_names = expected_skipped_test_cases_names or []

    passed_test_cases_names = set(
        passed_test_case.test_case_name for passed_test_case in testing_summary.passed
    )
    failed_test_cases_names = set(
        failed_test_case.test_case_name for failed_test_case in testing_summary.failed
    )
    broken_test_cases_names = set(
        broken_test_case.test_case_name for broken_test_case in testing_summary.broken
    )
    skipped_test_cases_names = set(
        skipped_test_case.test_case_name
        for skipped_test_case in testing_summary.skipped
    )

    for broken_test_case in testing_summary.broken_suites:
        for test_case_name in broken_test_case.test_case_names:
            broken_test_cases_names.add(test_case_name)

    actual = CairoTestCases(
        passed=passed_test_cases_names,
        failed=failed_test_cases_names,
        broken=broken_test_cases_names,
        skipped=skipped_test_cases_names,
    )

    expected = CairoTestCases(
        passed=set(expected_passed_test_cases_names),
        failed=set(expected_failed_test_cases_names),
        broken=set(expected_broken_test_cases_names),
        skipped=set(expected_skipped_test_cases_names),
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
        disable_hint_validation=False,
        cairo_path: Optional[List[Path]] = None,
        test_cases: Optional[List[str]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:
        ...


@pytest.fixture(name="log_color_provider", scope="module")
def log_color_provider_fixture() -> LogColorProvider:
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    return log_color_provider


@pytest.fixture(name="run_cairo_test_runner", scope="module")
def run_cairo_test_runner_fixture(
    session_mocker: MockerFixture, log_color_provider: LogColorProvider
) -> RunCairoTestRunnerFixture:
    async def run_cairo_test_runner(
        path: Path,
        seed: Optional[int] = None,
        disable_hint_validation=False,
        cairo_path: Optional[List[Path]] = None,
        test_cases: Optional[List[str]] = None,
        ignored_test_cases: Optional[List[str]] = None,
    ) -> TestingSummary:
        protostar_directory_mock = session_mocker.MagicMock()
        protostar_directory_mock.protostar_test_only_cairo_packages_path = Path()

        project_cairo_path_builder = cast(
            ProjectCairoPathBuilder, session_mocker.MagicMock()
        )
        project_cairo_path_builder.build_project_cairo_path_list = (
            lambda relative_cairo_path_list: relative_cairo_path_list
        )

        targets: List[str] = []
        if test_cases is None:
            targets.append(str(path))
        else:
            for test_case in test_cases:
                targets.append(f"{str(path)}::{test_case}")

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
            targets=targets,
            ignored_targets=ignored_targets,
            seed=seed,
            disable_hint_validation=disable_hint_validation,
            cairo_path=cairo_path or [],
        )

    return run_cairo_test_runner


class CreateProtostarProjectFixture(Protocol):
    def __call__(self) -> ContextManager[ProtostarFixture]:
        ...


@pytest.fixture(name="create_protostar_project", scope="module")
def create_protostar_project_fixture(
    session_mocker: MockerFixture,
    tmp_path_factory: TempPathFactory,
    signing_credentials: Tuple[str, str],
):
    @contextmanager
    def create_protostar_project():
        tmp_path = tmp_path_factory.mktemp("project_name")
        project_root_path = tmp_path / "project_name"
        cwd = Path().resolve()
        protostar = build_protostar_fixture(
            mocker=session_mocker,
            project_root_path=project_root_path,
            signing_credentials=signing_credentials,
        )

        protostar.init_sync()
        os.chdir(project_root_path)
        yield protostar
        os.chdir(cwd)

    return create_protostar_project


@pytest.fixture(name="get_abi_from_contract", scope="module")
def get_abi_from_contract_fixture(create_protostar_project) -> Callable[[str], AbiType]:
    def get_abi_from_contract(contract_source_code: str) -> AbiType:
        with create_protostar_project() as protostar:
            protostar.create_files({"src/main.cairo": contract_source_code})
            protostar.build_sync()
            with open("build/main_abi.json") as f:
                abi = json.load(f)
                return abi

    return get_abi_from_contract
