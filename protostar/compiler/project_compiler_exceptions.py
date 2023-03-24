from pathlib import Path

from protostar.protostar_exception import ProtostarException


class SourceFileNotFoundException(ProtostarException):
    def __init__(self, contract_path: Path):
        super().__init__(
            f"Couldn't find Cairo file `{contract_path.resolve()}`\n"
            'Did you forget to update protostar.toml::["protostar.contracts"]?'
        )


class CompilationException(ProtostarException):
    def __init__(self, contract_name: str, err: Exception):
        super().__init__(
            f"Protostar couldn't compile '{contract_name}' contract\n{str(err)}"
        )
