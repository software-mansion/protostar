from typing import Callable

from protostar.starknet import Cheatcode, CheatcodeException
from protostar.testing.test_config import TestConfig


class MaxExamplesCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        test_config: TestConfig,
    ):
        super().__init__(syscall_dependencies)
        self.test_config = test_config

    @property
    def name(self) -> str:
        return "max_examples"

    def build(self) -> Callable[[int], None]:
        return self.max_examples

    def max_examples(self, max_examples: int) -> None:
        if max_examples <= 0:
            raise CheatcodeException(self, "Max examples value must greater than 0.")

        self.test_config.fuzz_max_examples = max_examples
