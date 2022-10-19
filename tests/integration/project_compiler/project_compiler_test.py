import json
from pathlib import Path
from typing import cast, Any

import pytest
from pytest_mock import MockerFixture

from protostar.compiler import (
    CompilationException,
    ProjectCompiler,
    ProjectCompilerConfig,
)
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.configuration_file import FakeConfigurationFile
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection
from protostar.starknet.compiler.starknet_compilation import StarknetCompiler

CreateLoaderFixture = Any  # FIXME(arcticae): Properly type this fixture


@pytest.fixture(name="create_loader")
def create_loader_fixture(mocker: MockerFixture):
    def create_loader(return_value: Any) -> Any:
        load_mock = mocker.MagicMock()
        load_mock.return_value = return_value
        loader = mocker.MagicMock()
        cast(ProtostarTOMLSection.Loader, loader).load = load_mock
        return cast(ProtostarTOMLSection.Loader[Any], loader)

    return create_loader


def test_compiling(tmp_path: Path, datadir: Path, create_loader: CreateLoaderFixture):
    project_root_path = datadir / "importing"
    project_compiler = ProjectCompiler(
        project_root_path,
        project_cairo_path_builder=ProjectCairoPathBuilder(
            project_root_path,
            configuration_file=FakeConfigurationFile(
                lib_path=project_root_path / "modules"
            ),
        ),
        contracts_section_loader=create_loader(
            ProtostarContractsSection(
                contract_name_to_paths={"main": [Path("./entry_point.cairo")]}
            )
        ),
    )

    project_compiler.compile_project(output_dir=tmp_path)

    with open(str(tmp_path / "main.json"), mode="r", encoding="utf-8") as file:
        output = json.load(file)
        # Check the structure
        assert output["abi"]
        assert output["program"]

    with open(str(tmp_path / "main_abi.json"), mode="r", encoding="utf-8") as abi_file:
        # Check the ABI
        abi = json.load(abi_file)
        assert isinstance(abi, list)
        assert len(abi) == 1
        contract_function = abi[0]
        assert contract_function["name"] == "add_3"
        assert contract_function["type"] == "function"
        assert len(contract_function["inputs"]) == 1
        function_input = contract_function["inputs"][0]
        assert function_input["type"] == "felt"


def test_handling_cairo_errors(tmp_path: Path, datadir: Path, create_loader: CreateLoaderFixture):
    project_root_path = datadir / "compilation_error"

    with pytest.raises(CompilationException):
        ProjectCompiler(
            project_root_path=project_root_path,
            project_cairo_path_builder=ProjectCairoPathBuilder(
                project_root_path,
                configuration_file=FakeConfigurationFile(
                    lib_path=project_root_path / "modules"
                ),
            ),
            contracts_section_loader=create_loader(
                ProtostarContractsSection(
                    contract_name_to_paths={
                        "main": [project_root_path / "invalid_contract.cairo"]
                    }
                )
            ),
            default_config=ProjectCompilerConfig(
                relative_cairo_path=[project_root_path]
            ),
        ).compile_project(output_dir=tmp_path)


def test_handling_not_existing_main_files(tmp_path: Path, datadir: Path, create_loader: CreateLoaderFixture):
    project_root_path = datadir / "compilation_error"

    with pytest.raises(StarknetCompiler.FileNotFoundException):
        ProjectCompiler(
            project_root_path=project_root_path,
            project_cairo_path_builder=ProjectCairoPathBuilder(
                project_root_path,
                configuration_file=FakeConfigurationFile(
                    lib_path=project_root_path / "modules"
                ),
            ),
            contracts_section_loader=create_loader(
                ProtostarContractsSection(
                    contract_name_to_paths={
                        "main": [project_root_path / "NOT_EXISTING_FILE.cairo"]
                    }
                )
            ),
            default_config=ProjectCompilerConfig(
                relative_cairo_path=[project_root_path]
            ),
        ).compile_project(output_dir=tmp_path)
