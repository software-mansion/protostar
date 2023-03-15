# pylint: disable=duplicate-code
from typing import cast, Optional, Any, TYPE_CHECKING

from starkware.cairo.lang.compiler.preprocessor.flow import ReferenceManager
from starkware.cairo.lang.compiler.program import CairoHint
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import CallType, CallResult
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.core.os.syscall_handler import (
    DeprecatedBlSyscallHandler,
)
from starkware.starknet.core.os.syscall_utils import cast_to_int
from starkware.starknet.definitions.constants import GasCost
from starkware.starknet.security.secure_hints import HintsWhitelist
from starkware.starknet.services.api.contract_class.contract_class import EntryPointType

from protostar.starknet.address import Address
from protostar.starknet.selector import Selector

from protostar.cheatable_starknet.controllers.expect_call_controller import (
    ExpectedCall,
    ExpectCallController,
)

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


class CheatableSysCallHandlerException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CheatableSysCallHandler(DeprecatedBlSyscallHandler):
    def __init__(self, state: StateSyncifier, **kwargs: Any):
        self.cheatable_state: "CheatableCachedState" = cast(
            "CheatableCachedState", state.async_state
        )

        super().__init__(state=state, **kwargs)

    @property
    def block_info(self) -> BlockInfo:
        return self.cheatable_state.get_block_info(self.contract_address)

    @block_info.setter
    def block_info(self, block_info: BlockInfo):
        # Only called in constructor.
        assert block_info == self.cheatable_state.block_info

    def _get_caller_address(
        self,
        syscall_ptr: RelocatableValue,
    ) -> int:
        caller_address = super()._get_caller_address(syscall_ptr=syscall_ptr)
        pranked_address = self.cheatable_state.get_pranked_address(
            Address(self.contract_address)
        )
        return int(pranked_address) if pranked_address is not None else caller_address

    def _call_contract(self, syscall_ptr: RelocatableValue, syscall_name: str) -> CallResult:
        # Parse request and prepare the call.
        request = self._read_and_validate_syscall_request(
            syscall_name=syscall_name, syscall_ptr=syscall_ptr
        )
        calldata = self.segments.memory.get_range_as_ints(
            addr=request.calldata, size=request.calldata_size
        )

        code_address: Optional[int] = None
        class_hash: Optional[int] = None
        function_selector = Selector(cast(int, request.function_selector))
        if syscall_name == "call_contract":
            code_address = cast_to_int(request.contract_address)
            contract_address = code_address
            # region Modified Starknet code.
            if (
                    mocked_response := self.cheatable_state.get_mocked_response(
                        target_address=Address(contract_address),
                        entrypoint=function_selector,
                    )
            ) is not None:
                return CallResult(retdata=mocked_response, gas_consumed=0, failure_flag=0)
            # endregion

            caller_address = self.contract_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.CALL
        elif syscall_name == "delegate_call":
            code_address = cast_to_int(request.contract_address)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.DELEGATE
        elif syscall_name == "delegate_l1_handler":
            code_address = cast_to_int(request.contract_address)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.L1_HANDLER
            call_type = CallType.DELEGATE
        elif syscall_name == "library_call":
            class_hash = cast_to_int(request.class_hash)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.EXTERNAL
            call_type = CallType.DELEGATE
        elif syscall_name == "library_call_l1_handler":
            class_hash = cast_to_int(request.class_hash)
            contract_address = self.contract_address
            caller_address = self.caller_address
            entry_point_type = EntryPointType.L1_HANDLER
            call_type = CallType.DELEGATE
        else:
            raise NotImplementedError(f"Unsupported call type {syscall_name}.")

        # region Modified Starknet code.
        ExpectCallController.remove_expected_call_static(
            cheatable_state=self.cheatable_state,
            expected_call_to_remove=ExpectedCall(
                address=Address(contract_address),
                fn_selector=function_selector,
                calldata=calldata,
            ),
        )

        # endregion

        call = self.execute_entry_point_cls(
            call_type=call_type,
            class_hash=class_hash,
            contract_address=contract_address,
            code_address=code_address,
            entry_point_selector=cast_to_int(request.function_selector),
            initial_gas=GasCost.INITIAL.value,
            entry_point_type=entry_point_type,
            calldata=calldata,
            caller_address=caller_address,
        )

        return self.execute_entry_point(call=call)

    def _deploy(self, syscall_ptr: RelocatableValue) -> int:
        """
        Initializes and runs the constructor of the new contract.
        Returns the address of the newly deployed contract.
        """
        request = self._read_and_validate_syscall_request(
            syscall_name="deploy", syscall_ptr=syscall_ptr
        )
        assert request.deploy_from_zero in [
            0,
            1,
        ], "The deploy_from_zero field in the deploy system call must be 0 or 1."
        constructor_calldata = self.segments.memory.get_range_as_ints(
            addr=cast(RelocatableValue, request.constructor_calldata),
            size=cast_to_int(request.constructor_calldata_size),
        )
        class_hash = cast_to_int(request.class_hash)

        deployer_address = self.contract_address if request.deploy_from_zero == 0 else 0
        contract_address = calculate_contract_address_from_hash(
            salt=cast_to_int(request.contract_address_salt),
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=deployer_address,
        )

        # region Modified Starknet code.
        self.cheatable_state.contract_address_to_class_hash_map[
            Address(contract_address)
        ] = class_hash
        # endregion

        # Instantiate the contract.
        self.sync_state.deploy_contract(contract_address=contract_address, class_hash=class_hash)

        self.execute_constructor_entry_point(
            contract_address=contract_address,
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
        )

        return contract_address


class CheatableHintsWhitelist(HintsWhitelist):
    def verify_hint_secure(self, hint: CairoHint, reference_manager: ReferenceManager):
        pass
