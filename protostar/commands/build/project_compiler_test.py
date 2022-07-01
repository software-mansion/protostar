import json
from pathlib import Path

import pytest

from protostar.commands.build.build_exceptions import CairoCompilationException
from protostar.commands.build.project_compiler import ProjectCompiler
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.utils.starknet_compilation import StarknetCompiler


def test_compiling(tmp_path: Path, datadir: Path):
    project_root_path = datadir / "importing"

    ProjectCompiler(
        ProtostarProjectSection(libs_path=project_root_path / "lib"),
        ProtostarContractsSection(
            contract_name_to_paths={"main": [project_root_path / "entry_point.cairo"]}
        ),
    ).compile(
        output_dir=tmp_path,
        cairo_path=[project_root_path],
        disable_hint_validation=False,
    )

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
    project_root_path = datadir / "compilation_error"

    with pytest.raises(CairoCompilationException):
        ProjectCompiler(
            ProtostarProjectSection(libs_path=project_root_path / "lib"),
            ProtostarContractsSection(
                contract_name_to_paths={
                    "main": [project_root_path / "invalid_contract.cairo"]
                }
            ),
        ).compile(
            output_dir=tmp_path,
            cairo_path=[project_root_path],
            disable_hint_validation=False,
        )


def test_handling_not_existing_main_files(tmp_path: Path, datadir: Path):
    project_root_path = datadir / "compilation_error"

    with pytest.raises(StarknetCompiler.FileNotFoundException):
        ProjectCompiler(
            ProtostarProjectSection(libs_path=project_root_path / "lib"),
            ProtostarContractsSection(
                contract_name_to_paths={
                    "main": [project_root_path / "NOT_EXISTING_FILE.cairo"]
                }
            ),
        ).compile(
            output_dir=tmp_path,
            cairo_path=[project_root_path],
            disable_hint_validation=False,
        )
