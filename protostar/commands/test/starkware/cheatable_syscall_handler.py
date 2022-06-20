import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, cast

from starkware.cairo.common.structs import CairoStructProxy
from starkware.cairo.lang.vm.memory_segments import MemorySegmentManager
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.objects import CallType, OrderedEvent
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.core.os.syscall_utils import (
    BusinessLogicSysCallHandler,
    initialize_contract_state,
)
from starkware.starknet.security.secure_hints import HintsWhitelist
from starkware.starknet.services.api.contract_class import EntryPointType

from protostar.commands.test.starkware.types import AddressType, SelectorType

if TYPE_CHECKING:
    from protostar.commands.test.starkware.cheatable_state import CheatableCarriedState


class CheatableSysCallHandlerException(BaseException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CheatableSysCallHandler(BusinessLogicSysCallHandler):
    @property
    def cheatable_state(self):
        return cast("CheatableCarriedState", self.state)

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
        if target in self.cheatable_state.pranked_contracts_map:
            raise CheatableSysCallHandlerException(
                f"Contract with address {target} has been already pranked"
            )
        self.cheatable_state.pranked_contracts_map[target] = addr

    def reset_caller_address(self, target_contract_address: Optional[int] = None):
        target = (
            target_contract_address
            if target_contract_address
            else self.contract_address
        )
        if target not in self.cheatable_state.pranked_contracts_map:
            raise CheatableSysCallHandlerException(
                f"Contract with address {target} has not been pranked"
            )
        del self.cheatable_state.pranked_contracts_map[target]

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

        if self.contract_address in self.cheatable_state.pranked_contracts_map:
            return self.cheatable_state.pranked_contracts_map[self.contract_address]

        return self.caller_address

    def unregister_mock_call(
        self, contract_address: AddressType, selector: SelectorType
    ):
        if contract_address not in self.cheatable_state.mocked_calls_map:
            raise CheatableSysCallHandlerException(
                f"Contract {contract_address} doesn't have mocked selectors."
            )
        if selector not in self.cheatable_state.mocked_calls_map[contract_address]:
            raise CheatableSysCallHandlerException(
                f"Couldn't find mocked selector {selector} for an address {contract_address}."
            )
        del self.cheatable_state.mocked_calls_map[contract_address][selector]

    def get_contract_path_from_contract_address(
        self, contract_address: AddressType
    ) -> Optional[Path]:
        if (
            contract_address
            in self.cheatable_state.contract_address_to_contract_path_map
        ):
            return self.cheatable_state.contract_address_to_contract_path_map[
                contract_address
            ]

        if contract_address in self.cheatable_state.contract_address_to_class_hash_map:
            class_hash = self.cheatable_state.contract_address_to_class_hash_map[
                contract_address
            ]
            if class_hash in self.cheatable_state.class_hash_to_contract_path_map:
                return self.cheatable_state.class_hash_to_contract_path_map[class_hash]

        return None

    def _call_contract(
        self,
        segments: MemorySegmentManager,
        syscall_ptr: RelocatableValue,
        syscall_name: str,
    ) -> List[int]:
        request = self._read_and_validate_syscall_request(
            syscall_name=syscall_name, segments=segments, syscall_ptr=syscall_ptr
        )
        contract_address = cast(int, request.contract_address)

        if contract_address in self.cheatable_state.mocked_calls_map:
            if (
                request.function_selector
                in self.cheatable_state.mocked_calls_map[contract_address]
            ):
                return self.cheatable_state.mocked_calls_map[contract_address][
                    request.function_selector
                ]

        return self._call_contract_without_retrieving_request(
            segments, syscall_name, request
        )

    # copy of super().call_contract with removed call to _read_and_validate_syscall_request
    def _call_contract_without_retrieving_request(
        self,
        segments: MemorySegmentManager,
        syscall_name: str,
        request: CairoStructProxy,
    ) -> List[int]:

        calldata = segments.memory.get_range_as_ints(
            addr=request.calldata, size=request.calldata_size
        )

        code_address = None
        class_hash = None
        if syscall_name == "call_contract":
            code_address = cast(int, request.contract_address)
            contract_address = code_address
            caller_address = self.contract_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.CALL
        elif syscall_name == "delegate_call":
            code_address = cast(int, request.contract_address)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.DELEGATE
        elif syscall_name == "delegate_l1_handler":
            code_address = cast(int, request.contract_address)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.L1_HANDLER
            call_type = CallType.DELEGATE
        elif syscall_name == "library_call":
            class_hash = to_bytes(cast(int, request.class_hash))
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.DELEGATE
        elif syscall_name == "library_call_l1_handler":
            class_hash = to_bytes(cast(int, request.class_hash))
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.L1_HANDLER
            call_type = CallType.DELEGATE
        else:
            raise NotImplementedError(f"Unsupported call type {syscall_name}.")

        call = self.execute_entry_point_cls(
            call_type=call_type,
            class_hash=class_hash,
            contract_address=contract_address,
            code_address=code_address,
            entry_point_selector=cast(int, request.function_selector),
            entry_point_type=entry_point_type,
            calldata=calldata,
            caller_address=caller_address,
        )

        return self.execute_entry_point(call=call)

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

    def _deploy(
        self, segments: MemorySegmentManager, syscall_ptr: RelocatableValue
    ) -> int:
        request = self._read_and_validate_syscall_request(
            syscall_name="deploy", segments=segments, syscall_ptr=syscall_ptr
        )
        assert (
            request.reserved == 0
        ), "The reserved field in the deploy system call must be 0."
        constructor_calldata = segments.memory.get_range_as_ints(
            addr=cast(RelocatableValue, request.constructor_calldata),
            size=cast(int, request.constructor_calldata_size),
        )
        class_hash = cast(int, request.class_hash)

        contract_address = calculate_contract_address_from_hash(
            salt=cast(int, request.contract_address_salt),
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=self.contract_address,
        )

        # BEGIN: PROTOSTAR_MODIFICATION — update mappings
        self.cheatable_state.contract_address_to_class_hash_map[
            contract_address
        ] = class_hash
        # END: PROTOSTAR_MODIFICATION

        # Initialize the contract.
        class_hash_bytes = to_bytes(class_hash)
        future = asyncio.run_coroutine_threadsafe(
            coro=initialize_contract_state(
                state=self.state,
                class_hash=class_hash_bytes,
                contract_address=contract_address,
            ),
            loop=self.loop,
        )
        future.result()

        self.execute_constructor_entry_point(
            contract_address=contract_address,
            class_hash_bytes=class_hash_bytes,
            constructor_calldata=constructor_calldata,
        )

        # Update deployed contract addresses.
        self.deployed_contracts.append(contract_address)

        return contract_address


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, _hint, _reference_manager):
        return True
