from typing import Callable

from protostar.cheatable_starknet.controllers import ContractsController
from protostar.starknet import Address
from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)


class PrankHintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "start_prank"

    def _build(self) -> Callable:
        return self.start_prank

    def start_prank(self, caller_address: int, target_contract_address: int):
        valid_target_address = Address.from_user_input(target_contract_address)
        self._contracts_controller.prank(
            caller_address=Address.from_user_input(caller_address),
            target_address=valid_target_address,
        )
