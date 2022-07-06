from types import SimpleNamespace
from typing import Any

from protostar.starknet.hint_local import HintLocal
from protostar.commands.test.test_environment_exceptions import SimpleReportedException


class TestContext(SimpleNamespace):
    SUPPORTED_TYPES = (int, str, bool)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if not isinstance(__value, TestContext.SUPPORTED_TYPES):
            raise SimpleReportedException(
                (
                    f"(context.{__name}) Tried to store an unsupported type: '{type(__value).__name__}'\n"
                    f"Supported types: {[t.__name__ for t in TestContext.SUPPORTED_TYPES]}"
                )
            )

        if __name in vars(self):
            raise SimpleReportedException(
                (
                    f"'context' is immutable\n"
                    f"(context.{__name}) Tried to change value from '{getattr(self, __name)}' to '{__value}'"
                )
            )

        super().__setattr__(__name, __value)


class TestContextHintLocal(HintLocal):
    def __init__(self, test_context: TestContext) -> None:
        super().__init__()
        self._test_context = test_context

    @property
    def name(self) -> str:
        return "context"

    def build(self) -> Any:
        return self._test_context
