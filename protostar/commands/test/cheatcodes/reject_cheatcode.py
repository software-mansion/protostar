from typing import Any, Callable

import hypothesis
import hypothesis.errors

from protostar.starknet.cheatcode import Cheatcode


class RejectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reject"

    def build(self) -> Callable[..., Any]:
        return self.reject

    def reject(self) -> None:
        hypothesis.reject()
        return
