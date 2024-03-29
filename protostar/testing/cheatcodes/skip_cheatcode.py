from typing import Any, Callable, Optional

from protostar.starknet import Cheatcode


class SkipCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "skip"

    def build(self) -> Callable[..., Any]:
        return self.skip

    def skip(self, reason: Optional[str] = None) -> None:
        raise TestSkipped(reason)


class TestSkipped(BaseException):
    def __init__(self, reason: Optional[str] = None) -> None:
        self.reason = reason
        super().__init__(reason)
