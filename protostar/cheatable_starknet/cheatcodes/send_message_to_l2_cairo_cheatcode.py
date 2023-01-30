import asyncio
from typing import Optional

from protostar.starknet import RawAddress, Address, CairoData
from protostar.starknet.selector import Selector

from .cairo_cheatcode import CairoCheatcode


class SendMessageToL2CairoCheatcode(CairoCheatcode):
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
                self.controllers.contracts.send_message_to_l2(
                    from_l1_address=Address.from_user_input(from_address),
                    to_l2_address=Address.from_user_input(to_address),
                    selector=Selector(function_name),
                    payload=payload,
                )
            )

        return send_message_to_l2
