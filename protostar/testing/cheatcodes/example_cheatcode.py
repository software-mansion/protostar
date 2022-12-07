from typing import Any

from typing_extensions import Protocol

from protostar.starknet import Cheatcode
from protostar.testing.fuzzing.strategy_descriptor import StrategyDescriptor
from protostar.testing.test_config import TestConfig, TestMode


class ExampleCallable(Protocol):
    def __call__(self, **kwargs: StrategyDescriptor):
        ...


class ExampleCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        test_config: TestConfig,
    ):
        super().__init__(syscall_dependencies)
        self.test_config = test_config

    @property
    def name(self) -> str:
        return "example"

    def build(self) -> ExampleCallable:
        return self.example

    def example(self, **kwargs: Any) -> None:
        if self.test_config.mode is not TestMode.FUZZ:
            self.test_config.convert_mode_to(TestMode.PARAMETERIZED)

        self.test_config.fuzz_examples.append(kwargs)
