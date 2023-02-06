import asyncio
from typing import Optional

from protostar.cheatable_starknet.controllers.contracts import ContractsController
from protostar.starknet import RawAddress, Address, CairoData
from protostar.starknet.selector import Selector

from .callable_hint_local import CallableHintLocal


class SendMessageToL2HintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController) -> None:
        super().__init__()
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "send_message_to_l2"

    def _build(self):
        def send_message_to_l2(
            function_name: str,
            from_address: RawAddress,
            to_address: RawAddress,
            payload: Optional[CairoData] = None,
        ) -> None:
            asyncio.run(
                self._contracts_controller.send_message_to_l2(
                    from_l1_address=Address.from_user_input(from_address),
                    to_l2_address=Address.from_user_input(to_address),
                    selector=Selector(function_name),
                    payload=payload,
                )
            )

        return send_message_to_l2
