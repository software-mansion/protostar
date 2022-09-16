from typing import Callable

import hypothesis
from hypothesis.errors import UnsatisfiedAssumption

from protostar.starknet.cheatcode import Cheatcode
from protostar.test_runner.fuzzing.exceptions import HypothesisRejectException


class AssumeCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "assume"

    def build(self) -> Callable[[bool], None]:
        return self.assume

    def assume(self, condition: bool) -> None:
        try:
            hypothesis.assume(condition)
        except UnsatisfiedAssumption as reject_exc:
            raise HypothesisRejectException(reject_exc) from reject_exc
