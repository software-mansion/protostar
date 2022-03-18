from collections import defaultdict
from typing import Dict, List, cast

from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.transaction_execution_objects import (
    ContractCallResponse,
)
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.security.secure_hints import HintsWhitelist
from starkware.starknet.services.api.contract_definition import EntryPointType

AddressType = int
SelectorType = int


class CheatcodeException(BaseException):
    pass


class CheatableSysCallHandler(BusinessLogicSysCallHandler):
    # roll
    custom_block_number = None

    def set_block_number(self, blk_number):
        self.custom_block_number = blk_number

    def _get_block_number(self):
        return (
            self.custom_block_number
            if self.custom_block_number is not None
            else super()._get_block_number()
        )

    # warp
    custom_block_timestamp = None

    def set_block_timestamp(self, blk_timestamp):
        self.custom_block_timestamp = blk_timestamp

    def _get_block_timestamp(self):
        return (
            self.custom_block_timestamp
            if self.custom_block_timestamp is not None
            else super()._get_block_timestamp()
        )

    # prank
    custom_caller_address = None

    def set_caller_address(self, addr):
        self.custom_caller_address = addr

    def _get_caller_address(
        self,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
    ) -> int:
        if self.custom_caller_address is not None:
            self._read_and_validate_syscall_request(
                syscall_name="get_caller_address",
                segments=segments,
                syscall_ptr=syscall_ptr,
            )
            return self.custom_caller_address
        return super()._get_caller_address(segments, syscall_ptr)

    # mock_call
    mocked_calls: Dict[AddressType, Dict[SelectorType, List[int]]] = defaultdict(dict)

    def register_mock_call(
        self, contract_address: AddressType, selector: int, ret_data: List[int]
    ):
        self.mocked_calls[contract_address][selector] = ret_data

    def unregister_mock_call(self, contract_address: AddressType, selector: int):
        if contract_address not in self.mocked_calls:
            raise CheatcodeException(
                f"Contract {contract_address} doesn't have mocked selectors."
            )
        if selector not in self.mocked_calls[contract_address]:
            raise CheatcodeException(
                f"Couldn't find mocked selector {selector} for an address {contract_address}."
            )
        del self.mocked_calls[contract_address][selector]

    def _call_contract(
        self,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
        syscall_name: str,
    ) -> List[int]:
        request = self._read_and_validate_syscall_request(
            syscall_name=syscall_name, segments=segments, syscall_ptr=syscall_ptr
        )
        code_address = cast(int, request.contract_address)

        if code_address in self.mocked_calls:
            if request.function_selector in self.mocked_calls[code_address]:
                return self.mocked_calls[code_address][request.function_selector]

        return self._call_contract_without_retrieving_request(
            segments, syscall_name, request
        )

    # copy of super().call_contract with removed call to _read_and_validate_syscall_request
    def _call_contract_without_retrieving_request(
        self,
        segments: MemorySegmentManager,
        syscall_name: str,
        request,
    ) -> List[int]:
        # pylint: disable=import-outside-toplevel
        calldata = segments.memory.get_range_as_ints(
            addr=request.calldata, size=request.calldata_size
        )

        code_address = cast(int, request.contract_address)
        if syscall_name == "call_contract":
            contract_address = code_address
            caller_address = self.contract_address
            entry_point_type = EntryPointType.EXTERNAL
        elif syscall_name == "delegate_call":
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.EXTERNAL
        elif syscall_name == "delegate_l1_handler":
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.L1_HANDLER
        else:
            raise NotImplementedError(f"Unsupported call type {syscall_name}.")

        from starkware.starknet.business_logic.internal_transaction import (
            InternalInvokeFunction,
        )

        tx = InternalInvokeFunction(
            contract_address=contract_address,
            code_address=code_address,
            entry_point_selector=cast(int, request.function_selector),
            entry_point_type=entry_point_type,
            calldata=calldata,
            signature=self.signature,
            hash_value=0,
            caller_address=caller_address,
            nonce=None,
        )

        with self.contract_call_execution_context(
            tx=tx, called_contract_address=tx.contract_address
        ):
            # Execute contract call.
            execution_info = tx.execute_contract_function(
                state=self.state,
                general_config=self.general_config,
                loop=self.loop,
                tx_execution_context=self.tx_execution_context,
            )

        # Update execution info.
        self.l2_to_l1_messages.extend(execution_info.l2_to_l1_messages)
        call_response = ContractCallResponse(
            retdata=execution_info.retdata,
        )
        self.internal_call_responses.append(call_response)
        self.internal_calls.extend(execution_info.contract_calls)

        return call_response.retdata


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
