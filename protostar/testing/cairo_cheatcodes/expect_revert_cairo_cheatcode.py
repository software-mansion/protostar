from typing import Callable, Optional

from protostar.starknet import ForkableStarknet
from protostar.testing.cheatcodes import ExpectRevertContext
from protostar.testing.test_environment_exceptions import RevertableException

from .cairo_cheatcode import CairoCheatcode


class ExpectRevertCairoCheatcode(CairoCheatcode):
    def __init__(
        self,
        starknet: ForkableStarknet,
        context: ExpectRevertContext,
    ) -> None:
        super().__init__(starknet)
        self._context = context

    @property
    def name(self) -> str:
        return "expect_revert"

    def build(self) -> Callable:
        return self.expect_revert

    def expect_revert(
        self, error_type: Optional[str] = None, error_message: Optional[str] = None
    ):
        return self._context.expect_revert(
            RevertableException(error_type=error_type, error_message=error_message)
        )
