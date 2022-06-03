from collections import defaultdict
from typing import Dict, List, Optional, cast

from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import OrderedEvent
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.security.secure_hints import HintsWhitelist
from starkware.starknet.services.api.contract_class import EntryPointType

AddressType = int
SelectorType = int


class CheatableSysCallHandlerException(BaseException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


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

    def set_caller_address(
        self, addr: int, target_contract_address: Optional[int] = None
    ):
        target = (
            target_contract_address
            if target_contract_address
            else self.contract_address
        )
        if target in self.state.pranked_contracts_map:
            raise CheatableSysCallHandlerException(
                f"Contract with address {target} has been already pranked"
            )
        self.state.pranked_contracts_map[target] = addr

    def reset_caller_address(self, target_contract_address: Optional[int] = None):
        target = (
            target_contract_address
            if target_contract_address
            else self.contract_address
        )
        if target not in self.state.pranked_contracts_map:
            raise CheatableSysCallHandlerException(
                f"Contract with address {target} has not been pranked"
            )
        del self.state.pranked_contracts_map[target]

    def _get_caller_address(
        self,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
    ) -> int:
        self._read_and_validate_syscall_request(
            syscall_name="get_caller_address",
            segments=segments,
            syscall_ptr=syscall_ptr,
        )

        if self.contract_address in self.state.pranked_contracts_map:
            return self.state.pranked_contracts_map[self.contract_address]

        return self.caller_address

    # mock_call
    mocked_calls: Dict[AddressType, Dict[SelectorType, List[int]]] = defaultdict(dict)

    def register_mock_call(
        self, contract_address: AddressType, selector: int, ret_data: List[int]
    ):
        self.mocked_calls[contract_address][selector] = ret_data

    def unregister_mock_call(self, contract_address: AddressType, selector: int):
        if contract_address not in self.mocked_calls:
            raise CheatableSysCallHandlerException(
                f"Contract {contract_address} doesn't have mocked selectors."
            )
        if selector not in self.mocked_calls[contract_address]:
            raise CheatableSysCallHandlerException(
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

        call = self.execute_entry_point_cls(
            contract_address=contract_address,
            code_address=code_address,
            entry_point_selector=cast(int, request.function_selector),
            entry_point_type=entry_point_type,
            calldata=calldata,
            caller_address=caller_address,
        )

        with self.contract_call_execution_context(
            call=call, called_contract_address=contract_address
        ):
            # Execute contract call.
            call_info = call.sync_execute(
                state=self.state,
                general_config=self.general_config,
                loop=self.loop,
                tx_execution_context=self.tx_execution_context,
            )

        # Update execution info.
        self.internal_calls.append(call_info)

        return call_info.retdata

    def emit_event(self, segments: MemorySegmentManager, syscall_ptr: RelocatableValue):
        """
        Handles the emit_event system call.
        """
        request = self._read_and_validate_syscall_request(
            syscall_name="emit_event", segments=segments, syscall_ptr=syscall_ptr
        )

        self.events.append(
            OrderedEvent(
                order=self.tx_execution_context.n_emitted_events,
                keys=segments.memory.get_range_as_ints(
                    addr=cast(RelocatableValue, request.keys),
                    size=cast(int, request.keys_len),
                ),
                data=segments.memory.get_range_as_ints(
                    addr=cast(RelocatableValue, request.data),
                    size=cast(int, request.data_len),
                ),
            )
        )

        # Update events count.
        self.tx_execution_context.n_emitted_events += 1


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
