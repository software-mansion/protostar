# pylint: disable=invalid-name
from dataclasses import dataclass
from os import listdir
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import pytest
from pytest_mock import MockerFixture
from typing_extensions import Protocol

from protostar.commands.test.test_command import TestCommand
from protostar.commands.test.testing_summary import TestingSummary
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.compiler.project_compiler import ProjectCompiler, ProjectCompilerConfig
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from tests.conftest import run_devnet

# pylint: disable=unused-import
from tests.integration._conftest.standard_project_fixture import (
    project_root_path_fixture,
    standard_project_fixture,
    version_manager_fixture,
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
        return await TestCommand(
            project_root_path=Path(),
            protostar_directory=mocker.MagicMock(),
            project_cairo_path_builder=mocker.MagicMock(),
        ).test(targets=[str(path)], seed=seed, fuzz_max_examples=fuzz_max_examples)

    return run_cairo_test_runner


@pytest.fixture(name="project_compilation_output_path", scope="module")
def project_compilation_output_path_fixture(project_root_path: Path):
    output_path = project_root_path / "build"
    output_path.mkdir(exist_ok=True)
    return output_path


COMPILED_PROJECT_FIXTURE = "compiled_project"


class CompileProjectFixture(Protocol):
    def __call__(self, str_path_to_content: Dict[str, str]) -> None:
        ...


@pytest.fixture(name="compile_project", scope="module")
def compile_project_fixture(
    standard_project, project_root_path: Path
) -> CompileProjectFixture:
    def compile_project(str_path_to_content: Dict[str, str]):
        for relative_str_path, content in str_path_to_content.items():
            save_file(project_root_path / relative_str_path, content)

    return compile_project


def save_file(path: Path, content: str):
    with open(
        path,
        mode="w",
        encoding="utf-8",
    ) as output_file:
        output_file.write(content)


@pytest.fixture(name=COMPILED_PROJECT_FIXTURE, scope="module")
def compiled_project_fixture(
    project_root_path: Path, project_compilation_output_path: Path
):
    protostar_toml_reader = ProtostarTOMLReader(
        protostar_toml_path=project_root_path / "protostar.toml"
    )
    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        contracts_section_loader=ProtostarContractsSection.Loader(
            protostar_toml_reader=protostar_toml_reader
        ),
        project_cairo_path_builder=ProjectCairoPathBuilder(
            project_root_path,
            project_section_loader=ProtostarProjectSection.Loader(
                protostar_toml_reader
            ),
        ),
    )
    project_compiler.compile_project(
        output_dir=project_compilation_output_path,
        config=ProjectCompilerConfig(
            debugging_info_attached=True,
            hint_validation_disabled=True,
            relative_cairo_path=[],
        ),
    )
    output_files_count = len(listdir(project_compilation_output_path))
    assert output_files_count > 0, "Project didn't compile"
