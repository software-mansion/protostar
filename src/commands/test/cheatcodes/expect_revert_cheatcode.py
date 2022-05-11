from abc import ABC, abstractmethod
from typing import Callable, Optional

from src.commands.test.cheatcodes._cheatcode import Cheatcode
from src.commands.test.test_environment_exceptions import RevertableException


class RevertableTestingExecutionEnvironment(ABC):
    @abstractmethod
    def expect_revert(self, expected_error: RevertableException) -> Callable[[], None]:
        ...


class ExpectRevertCheatcode(Cheatcode):
    def __init__(
        self,
        revertable_testing_execution_environment: RevertableTestingExecutionEnvironment,
    ) -> None:
        self._revertable_testing_execution_environment = (
            revertable_testing_execution_environment
        )
        super().__init__()

    @property
    def name(self) -> str:
        return "expect_revert"

    def build(self) -> Callable:
        def expect_revert(
            error_type: Optional[str] = None, error_message: Optional[str] = None
        ):
            return self._revertable_testing_execution_environment.expect_revert(
                RevertableException(error_type=error_type, error_message=error_message)
            )

        return expect_revert
