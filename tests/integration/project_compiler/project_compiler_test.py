import json
from pathlib import Path

import pytest

from protostar.compiler import CompilationException, ProjectCompiler
from protostar.compiler.project_cairo_path_builder import ProjectCairoPathBuilder
from protostar.configuration_file import (
    ConfigurationFileV2,
    ConfigurationTOMLInterpreter,
)
from protostar.utils.starknet_compilation import StarknetCompiler


def create_project_compiler(project_root_path: Path, main_file_path_str: str):
    configuration_file = ConfigurationFileV2(
        file_path=Path(),
        project_root_path=project_root_path,
        configuration_file_interpreter=ConfigurationTOMLInterpreter(
            file_content=f"""
            [project]
            libs-path="./modules"

            [contracts]
            main=["{main_file_path_str}"]
        """
        ),
    )
    project_cairo_path_builder = ProjectCairoPathBuilder(
        configuration_file=configuration_file,
        project_root_path=project_root_path,
    )
    project_compiler = ProjectCompiler(
        project_root_path,
        configuration_file=configuration_file,
        project_cairo_path_builder=project_cairo_path_builder,
    )
    return project_compiler


def test_compiling(tmp_path: Path, datadir: Path):
    project_compiler = create_project_compiler(
        project_root_path=datadir / "importing",
        main_file_path_str="./entry_point.cairo",
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


def test_handling_cairo_errors(tmp_path: Path, datadir: Path):
    project_compiler = create_project_compiler(
        project_root_path=datadir / "compilation_error",
        main_file_path_str="./invalid_contract.cairo",
    )

    with pytest.raises(CompilationException):
        project_compiler.compile_project(output_dir=tmp_path)


def test_handling_not_existing_main_files(tmp_path: Path, datadir: Path):
    project_compiler = create_project_compiler(
        project_root_path=datadir / "compilation_error",
        main_file_path_str="./NOT_EXISTING_FILE.cairo",
    )

    with pytest.raises(StarknetCompiler.FileNotFoundException):
        project_compiler.compile_project(output_dir=tmp_path)
