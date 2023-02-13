from typing import Callable
from pathlib import Path
from enum import Enum

from tests.integration._conftest import ProtostarFixture

TEST_CONTRACTS_PATH = Path(__file__).parent / "contracts"


class RequestedFiles(str, Enum):
    input_enum_contract_cairo = "enum_contract.cairo"
    input_basic_starknet_contract_cairo = "basic_starknet_contract.cairo"
    input_basic_starknet_test_cairo = "basic_starknet_test.cairo"
    input_roll_test_cairo = "roll_test.cairo"
    output_sierra = "output.sierra"
    output_casm = "output.casm"


class PrepareFilesFixture:
    def __init__(self, protostar: ProtostarFixture):
        self.protostar = protostar

    def prepare_files(self, requested_files: list[RequestedFiles]):
        files = {}
        for file_item in requested_files:
            file_path = Path(TEST_CONTRACTS_PATH / file_item.value)
            contents = file_path.read_text() if file_path.exists() else ""
            file_with_ext = ".".join(file_item.name.rsplit("_", 1))
            files[file_item.name] = (Path(f"./src/{file_with_ext}"), contents)

        self.protostar.create_files(
            {str(path): contents for path, contents in files.values()}
        )
        files = {
            label: (Path(self.protostar.project_root_path / path), contents)
            for label, (path, contents) in files.items()
        }
        for path, _ in files.values():
            assert path.exists()
        return files


def check_compiler_function(
    compiler_function_to_test: Callable, input_path: Path, output_path: Path
):
    compiler_function_to_test(input_path, output_path)
    assert output_path.exists() and output_path.stat().st_size
    contents = compiler_function_to_test(input_path)
    assert contents
    with open(str(output_path), "r") as file:
        assert contents == "".join(file.readlines())
