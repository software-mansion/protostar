from typing import Callable, Any, Mapping, Optional

from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.execution.objects import CallType
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class import EntryPointType

from protostar.starknet import Cheatcode, CheatcodeException
from protostar.utils.data_transformer import CairoOrPythonData, from_python_transformer


class SendMessageToL2Cheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "send_message_to_l2"

    def build(self) -> Callable[..., Any]:
        return self.send_message_to_l2

    def send_message_to_l2(
        self,
        fn_name: str,
        contract_address: Optional[int] = None,
        l1_sender_address: Optional[int] = 0,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> None:
        contract_address = (
            contract_address if contract_address else self.contract_address
        )
        from_address = l1_sender_address

        class_hash = self.state.get_class_hash_at(contract_address)
        contract_class = self.state.get_contract_class(class_hash)

        if fn_name not in [
            fn["name"] for fn in contract_class.abi if fn["type"] == "l1_handler"
        ]:
            raise CheatcodeException(
                self,
                f"L1 handler {fn_name} was not found in contract (address: {hex(contract_address)}) ABI",
            )

        if isinstance(calldata, Mapping):
            transformer = from_python_transformer(contract_class.abi, fn_name, "inputs")
            calldata = transformer(
                {
                    **calldata,
                    "from_address": from_address,
                }
            )
        else:
            calldata = [from_address, *(calldata or [])]

        self.execute_entry_point(
            ExecuteEntryPoint.create(
                contract_address=contract_address,
                calldata=calldata,
                entry_point_selector=get_selector_from_name(fn_name),
                caller_address=from_address,
                entry_point_type=EntryPointType.L1_HANDLER,
                call_type=CallType.DELEGATE,
                class_hash=class_hash,
            )
        )
