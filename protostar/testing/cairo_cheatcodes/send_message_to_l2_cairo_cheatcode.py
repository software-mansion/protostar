from typing import Callable, Optional

from protostar.starknet import RawAddress, Address, CairoOrPythonData
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode


class SendMessageToL2CairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "send_message_to_l2"

    def build(self):
        def send_message_to_l2(
            fn_name: str,
            from_address: int = 0,
            to_address: Optional[int] = None,
            payload: Optional[CairoOrPythonData] = None,
        ) -> None:
            return None

        return send_message_to_l2
