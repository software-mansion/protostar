from pathlib import Path
from enum import Enum

from tests.integration._conftest import ProtostarFixture
from tests.data.cairo1_contracts import (
    CAIRO_BINDINGS_CONTRACT_ENUM,
    CAIRO_BINDINGS_TESTS,
    CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO,
    CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO_TEST,
    CAIRO_ROLL_TEST,
)


class RequestedFiles(Enum):
    input_contract_cairo = 1
    input_test_cairo = 2
    input_hello_contract_cairo = 3
    input_hello_test_cairo = 4
    input_roll_test_cairo = 5
    output_sierra = 6
    output_casm = 7


class PrepareFilesFixture:
    def __init__(self, protostar: ProtostarFixture):
        self.protostar = protostar

    def prepare_files(self, requested_files: list[RequestedFiles]):
        files = {}
        for file in requested_files:
            contents = ""
            if file == RequestedFiles.input_contract_cairo:
                contents = CAIRO_BINDINGS_CONTRACT_ENUM
            elif file == RequestedFiles.input_test_cairo:
                contents = CAIRO_BINDINGS_TESTS
            elif file == RequestedFiles.input_hello_contract_cairo:
                contents = CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO
            elif file == RequestedFiles.input_hello_test_cairo:
                contents = CAIRO_BINDINGS_CONTRACT_STARKNET_HELLO_TEST
            elif file == RequestedFiles.input_roll_test_cairo:
                contents = CAIRO_ROLL_TEST
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
