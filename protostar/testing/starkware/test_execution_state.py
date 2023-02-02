from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing_extensions import Self

from starkware.starknet.testing.starknet import Starknet

from protostar.compiler import ProjectCompiler
from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_config import TestConfig
from protostar.testing.test_context import TestContext
from protostar.testing.test_output_recorder import OutputRecorder
from protostar.testing.test_suite import TestCase


@dataclass
class TestExecutionState(ABC):
    starknet: Starknet
    stopwatch: Stopwatch
    output_recorder: OutputRecorder
    context: TestContext
    config: TestConfig
    project_compiler: ProjectCompiler

    @abstractmethod
    def determine_test_mode(self, test_case: TestCase):
        ...

    @abstractmethod
    def fork(self) -> Self:
        ...
