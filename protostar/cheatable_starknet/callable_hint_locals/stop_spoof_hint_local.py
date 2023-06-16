from typing import Callable

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers.transaction_info import (
    TransactionInfoController,
)
from protostar.starknet import Address


class StopSpoofHintLocal(CallableHintLocal):
    def __init__(self, transaction_info_controller: TransactionInfoController):
        self._transaction_info_controller = transaction_info_controller

    @property
    def name(self) -> str:
        return "stop_spoof"

    def _build(self) -> Callable:
        return self.stop_spoof

    def stop_spoof(
        self,
        contract_address: int,
    ):
        address = Address(contract_address)
        self._transaction_info_controller.cancel_spoof(address)
