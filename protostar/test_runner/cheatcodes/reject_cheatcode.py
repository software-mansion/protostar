from typing import Callable

import hypothesis
from hypothesis.errors import UnsatisfiedAssumption

from protostar.starknet.cheatcode import Cheatcode
from protostar.test_runner.fuzzing.exceptions import HypothesisRejectException


class RejectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reject"

    def build(self) -> Callable[[], None]:
        return self.reject

    def reject(self) -> None:
        try:
            hypothesis.reject()
        except UnsatisfiedAssumption as reject_exc:
            raise HypothesisRejectException(reject_exc) from reject_exc
