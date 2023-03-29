from typing import cast, Optional, Any

from starkware.cairo.lang.compiler.preprocessor.flow import ReferenceManager
from starkware.cairo.lang.compiler.program import CairoHint
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import CallType, CallResult
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.core.os.syscall_handler import DeprecatedBlSyscallHandler
from starkware.starknet.definitions.constants import GasCost
from starkware.starknet.security.secure_hints import HintsWhitelist
from starkware.starknet.services.api.contract_class.contract_class import EntryPointType

from protostar.starknet.types import SelectorType
from .cheatable_cached_state import CheatableCachedState, cheaters_of
from .address import Address


class CheatableSysCallHandlerException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CheatableSysCallHandler(DeprecatedBlSyscallHandler):
    def __init__(self, state: SyncState, **kwargs: Any):
        # This field must be set before entering super constructor,
        # because it calls the setter for the `block_info` property.
        self.cheaters = cheaters_of(state)

        super().__init__(state=state, **kwargs)

    # TODO(mkaput): Eradicate this property in favor of `cheaters`.
    @property
    def cheatable_state(self) -> CheatableCachedState:
        state_syncifier = self.sync_state
        assert isinstance(state_syncifier, StateSyncifier)

        async_state = state_syncifier.async_state
        assert isinstance(async_state, CheatableCachedState)

        return async_state

    @property
    def block_info(self) -> BlockInfo:
        return self.cheaters.block_info.get_for_contract(Address(self.contract_address))

    @block_info.setter
    def block_info(self, block_info: BlockInfo):
        # Only called in constructor.
        assert block_info == self.cheaters.block_info.base

    def _get_caller_address(
        self,
        syscall_ptr: RelocatableValue,
    ) -> int:
        caller_address = super()._get_caller_address(syscall_ptr=syscall_ptr)

        if self.contract_address in self.cheatable_state.pranked_contracts_map:
            return self.cheatable_state.pranked_contracts_map[self.contract_address]

        return caller_address

    def unregister_mock_call(self, contract_address: Address, selector: SelectorType):
        if contract_address not in self.cheatable_state.mocked_calls_map:
            raise CheatableSysCallHandlerException(
                f"Contract {contract_address} doesn't have mocked selectors."
            )
        if selector not in self.cheatable_state.mocked_calls_map[contract_address]:
            raise CheatableSysCallHandlerException(
                f"Couldn't find mocked selector {selector} for an address {contract_address}."
            )
        del self.cheatable_state.mocked_calls_map[contract_address][selector]

    def _call_contract(
        self,
        syscall_ptr: RelocatableValue,
        syscall_name: str,
    ) -> CallResult:
        # Parse request and prepare the call.
        request = self._read_and_validate_syscall_request(
            syscall_name=syscall_name, syscall_ptr=syscall_ptr
        )
        calldata = self.segments.memory.get_range_as_ints(
            addr=request.calldata, size=request.calldata_size
        )

        code_address: Optional[int] = None
        class_hash: Optional[int] = None
        if syscall_name == "call_contract":
            code_address = cast(int, request.contract_address)

            # region Modified Starknet code.
            if code_address in self.cheatable_state.mocked_calls_map:
                if (
                    request.function_selector
                    in self.cheatable_state.mocked_calls_map[code_address]
                ):
                    retdata = self.cheatable_state.mocked_calls_map[code_address][
                        request.function_selector
                    ]
                    return CallResult(retdata=retdata, failure_flag=0, gas_consumed=0)
            # endregion

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
            class_hash = cast(int, request.class_hash)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.DELEGATE
        elif syscall_name == "library_call_l1_handler":
            class_hash = cast(int, request.class_hash)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.L1_HANDLER
            call_type = CallType.DELEGATE
        else:
            raise NotImplementedError(f"Unsupported call type {syscall_name}.")

        # region Modified Starknet code.
        contract_calldata = (int(str(request.function_selector)), calldata)
        self.cheatable_state.unregister_expected_call(
            contract_address=Address(contract_address), calldata=contract_calldata
        )

        # endregion

        call = self.execute_entry_point_cls(
            call_type=call_type,
            class_hash=class_hash,
            contract_address=contract_address,
            code_address=code_address,
            entry_point_selector=cast(int, request.function_selector),
            entry_point_type=entry_point_type,
            calldata=calldata,
            caller_address=caller_address,
            initial_gas=GasCost.INITIAL.value,
        )

        return self.execute_entry_point(call=call)

    def _deploy(
        self,
        syscall_ptr: RelocatableValue,
    ) -> int:
        request = self._read_and_validate_syscall_request(
            syscall_name="deploy", syscall_ptr=syscall_ptr
        )
        assert request.deploy_from_zero in [
            0,
            1,
        ], "The deploy_from_zero field in the deploy system call must be 0 or 1."
        constructor_calldata = self.segments.memory.get_range_as_ints(
            addr=cast(RelocatableValue, request.constructor_calldata),
            size=cast(int, request.constructor_calldata_size),
        )
        class_hash = cast(int, request.class_hash)

        deployer_address = self.contract_address if request.deploy_from_zero == 0 else 0
        contract_address = calculate_contract_address_from_hash(
            salt=cast(int, request.contract_address_salt),
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=deployer_address,
        )

        # region Modified Starknet code.
        self.cheatable_state.contract_address_to_class_hash_map[
            Address(contract_address)
        ] = class_hash
        # endregion

        # Initialize the contract.
        self.sync_state.deploy_contract(
            contract_address=contract_address, class_hash=class_hash
        )

        self.execute_constructor_entry_point(
            contract_address=contract_address,
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
        )

        return contract_address


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, hint: CairoHint, reference_manager: ReferenceManager):
        pass
