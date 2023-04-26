from typing import Callable

from protostar.starknet import CheatcodeException
from protostar.cheatable_starknet.controllers.contracts import (
    ContractsCheaterException,
    ContractsController,
)
from protostar.starknet.data_transformer import CairoData

from .callable_hint_local import CallableHintLocal


class PrintHintLocal(CallableHintLocal):
    def __init__(self, controller: ContractsController):
        self._controller = controller

    @property
    def name(self) -> str:
        return "protostar_print"

    def _build(
        self,
    ) -> Callable[[CairoData], None]:
        return self.protostar_print

    def protostar_print(self, data: CairoData) -> None:
        try:
            self._controller.protostar_print(data=data)
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
