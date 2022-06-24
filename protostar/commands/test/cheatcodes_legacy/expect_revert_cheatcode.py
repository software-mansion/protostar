from typing import TYPE_CHECKING, Callable, Optional

from protostar.commands.test.cheatcodes_legacy._cheatcode import OldCheatcode
from protostar.commands.test.test_environment_exceptions import RevertableException

if TYPE_CHECKING:
    from protostar.commands.test.test_execution_environment import (
        TestExecutionEnvironment,
    )


class ExpectRevertCheatcode(OldCheatcode):
    def __init__(
        self,
        testing_execution_environment: "TestExecutionEnvironment",
    ) -> None:
        self._testing_execution_environment = testing_execution_environment
        super().__init__()

    @property
    def name(self) -> str:
        return "expect_revert"

    def build(self) -> Callable:
        def expect_revert(
            error_type: Optional[str] = None, error_message: Optional[str] = None
        ):
            return self._testing_execution_environment.expect_revert(
                RevertableException(error_type=error_type, error_message=error_message)
            )

        return expect_revert
