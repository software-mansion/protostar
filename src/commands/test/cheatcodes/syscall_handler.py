from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.core.os.syscall_utils import (
    BusinessLogicSysCallHandler,
)
from starkware.starknet.security.secure_hints import HintsWhitelist


class CheatableSysCallHandler(BusinessLogicSysCallHandler):
    # roll
    block_number_proxy = None

    def set_block_number(self, blk_number):
        self.block_number_proxy = blk_number

    def _get_block_number(self):
        return (
            self.block_number_proxy
            if self.block_number_proxy is not None
            else super()._get_block_number()
        )

    # warp
    block_timestamp_proxy = None

    def set_block_timestamp(self, blk_timestamp):
        self.block_timestamp_proxy = blk_timestamp

    def _get_block_timestamp(self):
        return (
            self.block_timestamp_proxy
            if self.block_timestamp_proxy is not None
            else super()._get_block_timestamp()
        )

    # prank
    caller_address_proxy = None

    def set_caller_address(self, addr):
        self.caller_address_proxy = addr

    def _get_caller_address(
        self,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
    ) -> int:
        if self.caller_address_proxy is not None:
            self._read_and_validate_syscall_request(
                syscall_name="get_caller_address",
                segments=segments,
                syscall_ptr=syscall_ptr,
            )
            return self.caller_address_proxy
        return super()._get_caller_address(segments, syscall_ptr)


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
