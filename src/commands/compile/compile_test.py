import json
from pathlib import Path

from src.commands.compile.compile import compile_contract

current_directory = Path(__file__).parent


def test_compile(tmp_path):
    sources_root = Path(current_directory, "mock_sources")
    output_path = Path(tmp_path, "mock_compiled.json")
    abi_output_path = Path(tmp_path, "mock_abi.json")

    with open(str(output_path), mode="w", encoding="utf-8") as output, open(
        str(abi_output_path), mode="w", encoding="utf-8"
    ) as abi_file:
        compile_contract(
            input_files=[Path(sources_root, "mock_entry_point.cairo")],
            libraries_root=Path(current_directory, "mock_lib_root"),
            output_file=output,
            output_abi_file=abi_file,
            cairo_path=[],
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
