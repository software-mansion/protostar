from types import SimpleNamespace
from typing import Any

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
