from typing import List, cast

from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.security.secure_hints import HintsWhitelist

address = int
selector = str


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
    mocked_calls: dict[address, dict[selector, List[int]]] = {}

    def register_mock_call(
        self, contract_address: address, calldata: str, retdata: List[int]
    ):
        if contract_address not in self.mocked_calls:
            self.mocked_calls[contract_address] = {}
        self.mocked_calls[contract_address][calldata] = retdata

    def _call_contract(
        self,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
        syscall_name: str,
    ) -> List[int]:
        request = self._read_and_validate_syscall_request(
            syscall_name=syscall_name, segments=segments, syscall_ptr=syscall_ptr
        )
        calldata = segments.memory.get_range_as_ints(
            addr=request.calldata, size=request.calldata_size
        )
        code_address = cast(int, request.contract_address)

        if code_address in self.mocked_calls:
            if calldata in self.mocked_calls[code_address]:
                return self.mocked_calls[code_address][calldata]

        return super()._call_contract(segments, syscall_ptr, syscall_name)


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
