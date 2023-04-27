from typing import Callable

from protostar.cheatable_starknet.controllers.io import protostar_print
from protostar.starknet.data_transformer import CairoData

from .callable_hint_local import CallableHintLocal


class PrintHintLocal(CallableHintLocal):
    @property
    def name(self) -> str:
        return "protostar_print"

    def _build(
        self,
    ) -> Callable[[CairoData], None]:
        return self.protostar_print

    def protostar_print(self, data: CairoData) -> None:
        protostar_print(data=data)
