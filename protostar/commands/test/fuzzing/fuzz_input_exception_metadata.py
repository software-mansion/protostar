from dataclasses import dataclass
from typing import Dict, Any

from protostar.commands.test.test_environment_exceptions import ExceptionMetadata


@dataclass(frozen=True)
class FuzzInputExceptionMetadata(ExceptionMetadata):
    inputs: Dict[str, Any]

    @property
    def name(self) -> str:
        return "falsifying example"

    def format(self) -> str:
        return "\n".join(f"{k} = {v!r}" for k, v in self.inputs.items())
