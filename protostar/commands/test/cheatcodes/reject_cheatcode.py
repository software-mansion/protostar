from typing import Callable

import hypothesis
from protostar.starknet.cheatcode import Cheatcode


class RejectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reject"

    def build(self) -> Callable[[], None]:
        return self.reject

    # pylint: disable=no-self-use
    def reject(self) -> None:
        hypothesis.reject()
