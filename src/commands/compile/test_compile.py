import json
import shutil
from pathlib import Path

import pytest

from src.commands.compile.compile import compile_contract


current_directory = Path(__file__).parent
mock_outputs = Path(current_directory, "mock_output")


@pytest.fixture(name="clear_mock_outputs")
def clear_mock_outputs():
    if mock_outputs.is_dir():
        shutil.rmtree("mock_output")
    mock_outputs.mkdir()


@pytest.mark.usefixtures("clear_mock_outputs")
def test_compile():
    sources_root = Path(current_directory, "mock_sources")
    with open(
        "mock_output/mock_compiled.json", mode="w", encoding="utf-8"
    ) as output, open(
        "mock_output/mock_abi.json", mode="w", encoding="utf-8"
    ) as abi_file:
        compile_contract(
            input_files=[Path(sources_root, "mock_entry_point.cairo")],
            libraries_root=Path(current_directory, "mock_lib_root"),
            output_file=output,
            output_abi_file=abi_file,
            cairo_path=[],
        )

    with open("mock_output/mock_compiled.json", mode="r", encoding="utf-8") as output:
        output = json.load(output)
        # Check the structure
        assert output["abi"]
        assert output["program"]

    with open("mock_output/mock_abi.json", mode="r", encoding="utf-8") as abi_file:
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
