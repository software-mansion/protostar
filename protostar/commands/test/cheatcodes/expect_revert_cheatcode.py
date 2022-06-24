from typing import TYPE_CHECKING, Callable, Optional

from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.test_environment_exceptions import RevertableException

if TYPE_CHECKING:
    from protostar.commands.test.test_execution_environment import (
        TestExecutionEnvironment,
    )


class ExpectRevertCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        testing_execution_environment: "TestExecutionEnvironment",
    ) -> None:
        super().__init__(syscall_dependencies)
        self._testing_execution_environment = testing_execution_environment

    @property
    def name(self) -> str:
        return "expect_revert"

    def build(self) -> Callable:
        return self.expect_revert

    def expect_revert(
        self, error_type: Optional[str] = None, error_message: Optional[str] = None
    ):
        return self._testing_execution_environment.expect_revert(
            RevertableException(error_type=error_type, error_message=error_message)
        )
