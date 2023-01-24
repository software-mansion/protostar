from abc import ABC
from dataclasses import dataclass
from typing import TypeVar, Any, Optional

from protostar.cairo.cairo_function_executor import CairoFunctionExecutor
from protostar.testing.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)

InvokeResultT = TypeVar("InvokeResultT")


@dataclass
class TestExecutionResult:
    execution_resources: Optional[ExecutionResourcesSummary]


class ExecutionEnvironment(CairoFunctionExecutor[InvokeResultT], ABC):
    def __init__(self, state: Any):
        self.state: Any = state
