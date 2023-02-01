from typing import Callable
from pathlib import Path
from enum import Enum

from tests.integration._conftest import ProtostarFixture

TEST_CONTRACTS_PATH = Path(__file__).parent / "contracts"


class RequestedFiles(Enum):
    input_enum_contract_cairo = 1
    input_basic_starknet_contract_cairo = 2
    input_basic_starknet_test_cairo = 3
    input_roll_test_cairo = 4
    output_sierra = 5
    output_casm = 6


class PrepareFilesFixture:
    def __init__(self, protostar: ProtostarFixture):
        self.protostar = protostar

    def prepare_files(self, requested_files: list[RequestedFiles]):
        files = {}
        for file in requested_files:
            input_path = ""
            if file == RequestedFiles.input_enum_contract_cairo:
                input_path = TEST_CONTRACTS_PATH / "enum_contract.cairo"
            elif file == RequestedFiles.input_basic_starknet_contract_cairo:
                input_path = TEST_CONTRACTS_PATH / "basic_starknet_contract.cairo"
            elif file == RequestedFiles.input_basic_starknet_test_cairo:
                input_path = TEST_CONTRACTS_PATH / "basic_starknet_test.cairo"
            elif file == RequestedFiles.input_roll_test_cairo:
                input_path = TEST_CONTRACTS_PATH / "roll_test.cairo"
            contents = ""
            if input_path:
                contents = Path(input_path).read_text()
            file_with_ext = ".".join(file.name.rsplit("_", 1))
            files[file.name] = (Path(f"./src/{file_with_ext}"), contents)

        self.protostar.create_files(
            {str(path): contents for _, (path, contents) in files.items()}
        )
        files = {
            label: (Path(self.protostar.project_root_path / path), contents)
            for label, (path, contents) in files.items()
        }
        for _, (path, _) in files.items():
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
