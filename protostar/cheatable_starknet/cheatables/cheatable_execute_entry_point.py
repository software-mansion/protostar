# FIXME: Probably code of execute entry point was changed. THIS FILE NEEDS TO BE UPDATED
# pylint: disable=duplicate-code
import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple, cast, Any
from copy import deepcopy

from starkware.starknet.business_logic.execution.objects import (
    CallType,
    CallInfo,
    TransactionExecutionContext,
    ExecutionResourcesManager,
)
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.security import SecurityError
from starkware.cairo.lang.vm.utils import ResourcesError
from starkware.cairo.lang.vm.vm_exceptions import (
    HintException,
    VmException,
    VmExceptionBase,
)
from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
    EntryPointArgs,
)
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import State, SyncState
from starkware.starknet.business_logic.utils import (
    validate_contract_deployed,
    get_call_result_for_version0_class,
)
from starkware.starknet.core.os import os_utils
from starkware.starknet.core.os.syscall_handler import BusinessLogicSyscallHandler
from starkware.starknet.core.os.syscall_utils import HandlerException
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import (
    StarknetGeneralConfig,
    STARKNET_LAYOUT_INSTANCE,
)
from starkware.starknet.public import abi as starknet_abi
from starkware.starkware_utils.error_handling import (
    StarkException,
    wrap_with_stark_exception,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    EntryPointType,
    DeprecatedCompiledClass,
)

from protostar.starknet import Address
from protostar.cheatable_starknet.controllers.transaction_revert_exception import (
    TransactionRevertException,
)
from protostar.starknet.selector import Selector

from .cheatable_syscall_handler import CheatableSysCallHandler

FAULTY_CLASS_HASH = to_bytes(
    0x1A7820094FEAF82D53F53F214B81292D717E7BB9A92BB2488092CD306F3993F
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CheatableExecuteEntryPoint(ExecuteEntryPoint):
    max_steps: Optional[int] = None
    "``None`` means default Cairo value."

    @classmethod
    def create_for_protostar(
        cls,
        contract_address: Address,
        calldata: list[int],
        entry_point_selector: Selector,
        entry_point_type: EntryPointType = EntryPointType.EXTERNAL,
        call_type: CallType = CallType.CALL,
        class_hash: Optional[bytes] = None,
        caller_address: Optional[Address] = None,
    ):
        return cls.create_for_testing(
            entry_point_selector=int(entry_point_selector),
            calldata=calldata,
            contract_address=int(contract_address),
            entry_point_type=entry_point_type,
            call_type=call_type,
            caller_address=int(caller_address or Address(0)),
            class_hash=class_hash,
        )

    def _execute_version0_class(
        self,
        state: SyncState,
        resources_manager: ExecutionResourcesManager,
        tx_execution_context: TransactionExecutionContext,
        class_hash: int,
        compiled_class: DeprecatedCompiledClass,
        general_config: StarknetGeneralConfig,
    ) -> CallInfo:
        # Fix the current resources usage, in order to calculate the usage of this run at the end.
        previous_cairo_usage = resources_manager.cairo_usage

        # Prepare runner.
        with wrap_with_stark_exception(code=StarknetErrorCode.SECURITY_ERROR):
            runner = CairoFunctionRunner(
                program=compiled_class.program,
                layout=STARKNET_LAYOUT_INSTANCE.layout_name,
            )

        # Prepare implicit arguments.
        implicit_args = os_utils.prepare_os_implicit_args_for_version0_class(
            runner=runner
        )

        # Prepare syscall handler.
        initial_syscall_ptr = cast(
            RelocatableValue, implicit_args[starknet_abi.SYSCALL_PTR_OFFSET_IN_VERSION0]
        )

        # region Modified Starknet code.
        assert isinstance(
            state, StateSyncifier
        ), "Sync state is not a state syncifier!"  # This should always be true
        syscall_handler = CheatableSysCallHandler(
            execute_entry_point_cls=CheatableExecuteEntryPoint,
            tx_execution_context=tx_execution_context,
            state=state,
            resources_manager=resources_manager,
            caller_address=self.caller_address,
            contract_address=self.contract_address,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
            segments=runner.segments,
        )
        # endregion

        # Prepare all arguments.
        entry_point_args: EntryPointArgs = [
            self.entry_point_selector,
            implicit_args,
            len(self.calldata),
            # Allocate and mark the segment as read-only (to mark every input array as read-only).
            syscall_handler._allocate_segment(data=self.calldata),
        ]

        # Get offset to run from.
        entry_point = self._get_selected_entry_point(
            compiled_class=compiled_class, class_hash=class_hash
        )
        entry_point_offset = entry_point.offset

        # Run.
        self._run(
            runner=runner,
            entry_point_offset=entry_point_offset,
            entry_point_args=entry_point_args,
            hint_locals={"syscall_handler": syscall_handler},
            run_resources=tx_execution_context.run_resources,
            allow_tmp_segments=False,
        )

        # Complete validations.
        os_utils.validate_and_process_os_context_for_version0_class(
            runner=runner,
            syscall_handler=syscall_handler,
            initial_os_context=implicit_args,
        )

        # Update resources usage (for the bouncer and fee calculation).
        resources_manager.cairo_usage += runner.get_execution_resources()

        # Build and return the call info.
        return self._build_call_info(
            storage=syscall_handler.starknet_storage,
            events=syscall_handler.events,
            l2_to_l1_messages=syscall_handler.l2_to_l1_messages,
            internal_calls=syscall_handler.internal_calls,
            execution_resources=resources_manager.cairo_usage - previous_cairo_usage,
            result=get_call_result_for_version0_class(runner=runner),
            class_hash=class_hash,
        )

    async def execute_for_testing(
        self,
        state: State,
        general_config: StarknetGeneralConfig,
        resources_manager: Optional[ExecutionResourcesManager] = None,
        tx_execution_context: Optional[TransactionExecutionContext] = None,
    ) -> CallInfo:
        try:
            return await super().execute_for_testing(
                state=state,
                general_config=self._change_max_steps_in_general_config(general_config),
                resources_manager=resources_manager,
                tx_execution_context=tx_execution_context,
            )
        except StarkException as ex:
            raise self._wrap_stark_exception(ex)

    def execute(
        self,
        state: SyncState,
        resources_manager: ExecutionResourcesManager,
        general_config: StarknetGeneralConfig,
        tx_execution_context: TransactionExecutionContext,
        support_reverted: bool = False,
    ):
        try:
            return super().execute(
                state=state,
                resources_manager=resources_manager,
                tx_execution_context=tx_execution_context,
                general_config=self._change_max_steps_in_general_config(general_config),
                support_reverted=support_reverted,
            )
        except StarkException as ex:
            raise self._wrap_stark_exception(ex)

    def _change_max_steps_in_general_config(
        self, general_config: StarknetGeneralConfig
    ):
        new_config = deepcopy(general_config)
        if self.max_steps is not None:
            # Providing a negative value to Protostar results in infinite steps,
            # this is here to mimic default Cairo behavior
            value = None if self.max_steps < 0 else self.max_steps
            # NOTE: We are doing it this way to avoid TypeError from typeguard
            new_config.__dict__["invoke_tx_max_n_steps"] = value
        return new_config

    def _wrap_stark_exception(self, stark_exception: StarkException):
        # This code is going change once Starknet is integrated with Cairo 1.
        message = stark_exception.message or ""
        results = re.findall("Error message: (.*)", message)
        if len(results) > 0:
            message = results[0]
        return TransactionRevertException(message=message, raw_ex=stark_exception)
