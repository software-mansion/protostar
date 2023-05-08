from typing import Callable

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers import ContractsController
from protostar.starknet import Address


class StopPrankHintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "stop_prank"

    def _build(self) -> Callable:
        return self.stop_prank

    def stop_prank(self, target_contract_address: int):
        address = Address.from_user_input(target_contract_address)
        self._contracts_controller.cancel_prank(target_address=address)
