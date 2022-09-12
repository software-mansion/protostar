from typing import Any, Callable

from protostar.starknet.cheatcode import Cheatcode

from protostar.commands.test.test_environment_exceptions import (
    SimpleSkippingReportedException,
)


class SkipCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "skip"

    def build(self) -> Callable[..., Any]:
        return self.skip

    # pylint: disable=no-self-use
    def skip(self, condition: bool = True, reason: str = "") -> None:
        if condition:
            raise SimpleSkippingReportedException(reason)
