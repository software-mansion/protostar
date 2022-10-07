from typing import Callable, Any, Mapping, Optional, List

from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.execution.objects import CallType
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class import EntryPointType, ContractClass

from protostar.starknet import Cheatcode, CheatcodeException
from protostar.utils.data_transformer import CairoOrPythonData, from_python_transformer


def get_calldata_for_execution(
        payload: CairoOrPythonData,
        l1_sender_address: int,
        contract_class: ContractClass,
        fn_name: str,
    ) -> List[int]:
    if isinstance(payload, Mapping):
        transformer = from_python_transformer(contract_class.abi, fn_name, "inputs")
        return transformer(
            {
                **payload,
                "from_address": l1_sender_address,
            }
        )
    return [l1_sender_address, *(payload or [])]


def get_contract_l1_handlers_names(contract_class: ContractClass) -> List[str]:
    return [
        fn["name"] for fn in contract_class.abi if fn["type"] == "l1_handler"
    ]


class SendMessageToL2Cheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "send_message_to_l2"

    def build(self) -> Callable[..., Any]:
        return self.send_message_to_l2

    def send_message_to_l2(
        self,
        fn_name: str,
        from_address: int = 0,
        to_address: Optional[int] = None,
        payload: Optional[CairoOrPythonData] = None,
    ) -> None:
        to_address = (
            to_address if to_address else self.contract_address
        )

        class_hash = self.state.get_class_hash_at(to_address)
        contract_class = self.state.get_contract_class(class_hash)

        if not contract_class.abi:
            raise CheatcodeException(self, "Contract (address: {hex(contract_address)}) doesn't have any entrypoints")

        if fn_name not in get_contract_l1_handlers_names(contract_class):
            raise CheatcodeException(
                self,
                f"L1 handler {fn_name} was not found in contract (address: {hex(to_address)}) ABI",
            )

        calldata = get_calldata_for_execution(payload, from_address, contract_class, fn_name)

        self.execute_entry_point(
            ExecuteEntryPoint.create(
                contract_address=to_address,
                calldata=calldata,
                entry_point_selector=get_selector_from_name(fn_name),
                # FIXME(arcticae): This might be wrong, since the caller might be some starknet OS specific address
                caller_address=from_address,
                entry_point_type=EntryPointType.L1_HANDLER,
                call_type=CallType.DELEGATE,
                class_hash=class_hash,
            )
        )
