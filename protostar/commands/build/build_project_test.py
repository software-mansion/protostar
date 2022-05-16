import json
from pathlib import Path

import pytest

from protostar.commands.build import build_project
from protostar.commands.build.build_exceptions import CairoCompilationException
from protostar.utils.config.project_test import make_mock_project
from protostar.utils.starknet_compilation import StarknetCompiler

current_directory = Path(__file__).parent


def test_build(tmp_path, mocker):
    libs_path = str(Path(current_directory, "mock_lib_root"))
    contracts = {
        "main": [f"{str(current_directory)}/mock_sources/mock_entry_point.cairo"]
    }
    project_mock = make_mock_project(mocker, contracts, libs_path, current_directory)

    build_project(
        output_dir=tmp_path,
        cairo_path=[],
        project=project_mock,
        disable_hint_validation=False,
    )

    output_path = Path(tmp_path, "main.json")
    abi_output_path = Path(tmp_path, "main_abi.json")

    with open(str(output_path), mode="r", encoding="utf-8") as output:
        output = json.load(output)
        # Check the structure
        assert output["abi"]
        assert output["program"]

    with open(str(abi_output_path), mode="r", encoding="utf-8") as abi_file:
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


def test_handling_cairo_errors(mocker, tmp_path):
    libs_path = str(Path(current_directory, "mock_lib_root"))
    contracts = {
        "main": [f"{str(current_directory)}/mock_sources/compilation_error.cairo"]
    }
    project_mock = make_mock_project(mocker, contracts, libs_path, current_directory)

    with pytest.raises(CairoCompilationException):
        build_project(
            output_dir=tmp_path,
            cairo_path=[],
            project=project_mock,
            disable_hint_validation=False,
        )


def test_handling_not_existing_main_files(mocker, tmp_path):
    libs_path = str(Path(current_directory, "mock_lib_root"))
    contracts = {"main": [f"{str(current_directory)}/NOT_EXISTING_MOCK.cairo"]}
    project_mock = make_mock_project(mocker, contracts, libs_path, current_directory)

    with pytest.raises(StarknetCompiler.FileNotFoundException):
        build_project(
            output_dir=tmp_path,
            cairo_path=[],
            project=project_mock,
            disable_hint_validation=False,
        )
