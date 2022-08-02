from typing import Any

from typing_extensions import Protocol

from protostar.commands.test.fuzzing.exceptions import FuzzingError
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor
from protostar.commands.test.fuzzing.strategy_selector import StrategySelector
from protostar.starknet.cheatcode import Cheatcode


class GivenCallable(Protocol):
    def __call__(self, **kwargs: StrategyDescriptor):
        ...


class GivenCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        strategy_selector: StrategySelector,
    ):
        super().__init__(syscall_dependencies)
        self.strategy_selector = strategy_selector

    @property
    def name(self) -> str:
        return "given"

    def build(self) -> GivenCallable:
        return self.given

    def given(self, **kwargs: Any) -> None:
        # Early check that all parameters names are valid explicitly.
        for param in kwargs:
            self.strategy_selector.check_exists(param)

        for param, descriptor in kwargs.items():
            # Raise nice error if got object which is not a strategy descriptor.
            if not isinstance(descriptor, StrategyDescriptor):
                raise FuzzingError(
                    f"Parameter {param} cannot be fuzzed: "
                    f"Type {type(descriptor)} is not a valid fuzzing strategy."
                )

            self.strategy_selector.set_strategy_descriptor(param, descriptor)
