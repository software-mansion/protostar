from typing import Literal, Any
from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider

JsonData = dict[str, Any]


@dataclass
class TestCaseResultMessage(StructuredMessage):
    type: str
    status: Literal["passed", "failed", "broken", "skipped", "unexpected_exception"]

    def format_human(self, fmt: LogColorProvider) -> str:
        assert False

    def format_dict(self) -> dict:
        assert False


def get_formatted_execution_time(execution_time: float) -> str:
    return f"{execution_time:.2f}"