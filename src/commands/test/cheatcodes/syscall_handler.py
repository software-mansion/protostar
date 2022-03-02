from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.security.secure_hints import HintsWhitelist


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

    def read_storage(
        self,
        address: int,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
    ):
        request = self._read_and_validate_syscall_request(
            syscall_name="storage_read", segments=segments, syscall_ptr=syscall_ptr
        )

        value = self._storage_read(address)
        response = self.structs.StorageReadResponse(value=value)

        self._write_syscall_response(
            syscall_name="StorageRead",
            response=response,
            segments=segments,
            syscall_ptr=syscall_ptr,
        )


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
