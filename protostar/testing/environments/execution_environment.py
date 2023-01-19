from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Optional

from protostar.testing.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)

InvokeResultT = TypeVar("InvokeResultT")


@dataclass
class TestExecutionResult:
    execution_resources: Optional[ExecutionResourcesSummary]


class ExecutionEnvironment(ABC, Generic[InvokeResultT]):
    def __init__(self, state: Any):
        self.state: Any = state

    @abstractmethod
    async def execute(self, function_name: str) -> InvokeResultT:
        ...
