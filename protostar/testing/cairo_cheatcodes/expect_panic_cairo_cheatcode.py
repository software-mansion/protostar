from typing import Callable, Optional

from protostar.starknet import ForkableStarknet
from protostar.testing.cheatcodes import ExpectRevertContext
from protostar.testing.test_environment_exceptions import RevertableException

from .cairo_cheatcode import CairoCheatcode


class ExpectPanicCairoCheatcode(CairoCheatcode):
    def __init__(
        self,
        starknet: ForkableStarknet,
        context: ExpectRevertContext,
    ) -> None:
        super().__init__(starknet)
        self._context = context

    @property
    def name(self) -> str:
        return "expect_panic"

    def build(self) -> Callable:
        return self.expect_panic

    def expect_panic(self, error_message: Optional[str] = None) -> None:
        self._context.expect_revert(
            RevertableException(error_type=None, error_message=error_message)
        )
