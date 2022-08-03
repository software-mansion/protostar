from typing import Any

from typing_extensions import Protocol

from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor
from protostar.commands.test.fuzzing.strategy_selector import StrategySelector
from protostar.commands.test.test_environment_exceptions import CheatcodeException
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

        learned = False

        for param, descriptor in kwargs.items():
            # Raise nice error if got object which is not a strategy descriptor.
            if not isinstance(descriptor, StrategyDescriptor):
                raise CheatcodeException(
                    "given",
                    f"Parameter {param} cannot be fuzzed: "
                    f"Type {type(descriptor)} is not a valid fuzzing strategy.",
                )

            learned |= self.strategy_selector.learn(param, descriptor)

        if learned:
            raise StrategyLearnedException


class StrategyLearnedException(BaseException):
    """
    An exception raised from the ``given`` cheatcode, indicating that the set of fuzzing strategies
    has changed (fuzzer _learned_ a new strategy).

    The expected behaviour is to let fuzzer catch this exception and restart fuzzing with new
    set of input parameter strategies.
    """
