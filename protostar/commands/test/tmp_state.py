from types import SimpleNamespace
from typing import Any

from protostar.commands.test.test_environment_exceptions import SimpleReportedException


# TODO: rename
class TmpState(SimpleNamespace):
    SUPPORTED_TYPES = (int, str, bool)

    # TODO: fix context.__deepcopy__
    def __getattr__(self, __name: str) -> Any:
        if __name not in vars(self):
            raise SimpleReportedException(
                (
                    f"Tried to read undefined value.\n"
                    f"Did you define 'context.{__name}' in the '__setup__' function?"
                )
            )

    def __setattr__(self, __name: str, __value: Any) -> None:
        if not isinstance(__value, TmpState.SUPPORTED_TYPES):
            raise SimpleReportedException(
                (
                    f"(context.{__name}) Tried to store an unsupported type: '{type(__value).__name__}'\n"
                    f"Supported types: {[t.__name__ for t in TmpState.SUPPORTED_TYPES]}"
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
