from typing import Any

from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.starknet.cheatcode import Cheatcode
from protostar.test_runner.fuzzing.strategy_descriptor import StrategyDescriptor
from protostar.test_runner.test_config import TestConfig, TestMode


class GivenCallable(Protocol):
    def __call__(self, **kwargs: StrategyDescriptor):
        ...


class GivenCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        test_config: TestConfig,
    ):
        super().__init__(syscall_dependencies)
        self.test_config = test_config

    @property
    def name(self) -> str:
        return "given"

    def build(self) -> GivenCallable:
        return self.given

    def given(self, **kwargs: Any) -> None:
        self.test_config.convert_mode_to(TestMode.FUZZ)

        for param, descriptor in kwargs.items():
            # Raise nice error if got object which is not a strategy descriptor.
            if not isinstance(descriptor, StrategyDescriptor):
                raise CheatcodeException(
                    self,
                    f"Parameter {param} cannot be fuzzed: "
                    f"Type {type(descriptor)} is not a valid fuzzing strategy.",
                )

            # Raise an error if user is trying to reassign a strategy descriptor.
            # While this is not a big problem for us, it is a rare situation that somebody
            # might want to do this explicitly, and more often this is just a typo bug.
            if param in self.test_config.fuzz_declared_strategies:
                raise CheatcodeException(
                    self,
                    f"Parameter {param} has been reassigned a fuzzing strategy. "
                    "Perhaps there is a typo in test case code?",
                )

            self.test_config.fuzz_declared_strategies[param] = descriptor
