import json
from pathlib import Path

from src.commands.build import build_project
from src.utils.config.package import PackageConfig, Package

current_directory = Path(__file__).parent


def test_build(tmp_path, mocker):
    package = Package(current_directory)

    mock_config = PackageConfig(
        name="",
        description="",
        license="",
        version="",
        authors=[""],
        contracts={
            "main": [
                f"{str(current_directory)}/mock_sources/mock_entry_point.cairo"
            ]
        },
        libs_path=str(Path(current_directory, "mock_lib_root")),
    )
    mocker.patch.object(package, attribute="load_config").return_value = mock_config

    output_path = Path(tmp_path, "main.json")
    abi_output_path = Path(tmp_path, "main_abi.json")

    build_project(
        output_dir=tmp_path,
        cairo_path=[],
        pkg=package,
    )

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
