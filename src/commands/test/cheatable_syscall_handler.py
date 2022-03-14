from collections import defaultdict
from typing import Dict, List, cast

from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.security.secure_hints import HintsWhitelist

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

        return super()._call_contract(segments, syscall_ptr, syscall_name)


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
