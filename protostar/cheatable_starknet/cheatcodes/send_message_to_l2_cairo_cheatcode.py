import asyncio
from typing import Optional

from protostar.starknet import RawAddress, Address, CairoOrPythonData
from protostar.starknet.selector import Selector

from .cairo_cheatcode import CairoCheatcode


class SendMessageToL2CairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "send_message_to_l2"

    def build(self):
        def send_message_to_l2(
            function_name: str,
            from_address: RawAddress,
            to_address: RawAddress,
            payload: Optional[CairoOrPythonData] = None,
        ) -> None:
            asyncio.run(
                self.cheaters.contracts.send_message_to_l2(
                    cheaters=self.cheaters,
                    from_l1_address=Address.from_user_input(from_address),
                    to_l2_address=Address.from_user_input(to_address),
                    selector=Selector(function_name),
                    payload=payload,
                )
            )

        return send_message_to_l2
