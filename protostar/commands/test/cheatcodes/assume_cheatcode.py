from typing import Callable

import hypothesis
from protostar.starknet.cheatcode import Cheatcode


class AssumeCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "assume"

    def build(self) -> Callable[[bool], None]:
        return self.assume

    # pylint: disable=no-self-use
    def assume(self, condition: bool) -> None:
        hypothesis.assume(condition)
