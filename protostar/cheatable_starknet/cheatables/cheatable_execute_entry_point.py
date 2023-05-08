# pylint: disable=duplicate-code,protected-access
import dataclasses
import logging
import re
from dataclasses import dataclass
from typing import Optional, cast, List
from copy import deepcopy

from starkware.starknet.builtins.segment_arena.segment_arena_builtin_runner import (
    SegmentArenaBuiltinRunner,
)
from starkware.starknet.business_logic.execution.objects import (
    CallType,
    CallInfo,
    TransactionExecutionContext,
    ExecutionResourcesManager,
)
from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.relocatable import RelocatableValue, MaybeRelocatable
from starkware.python.utils import to_bytes, as_non_optional
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
    EntryPointArgs,
)
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import State, SyncState
from starkware.starknet.business_logic.utils import (
    get_call_result_for_version0_class,
    get_call_result,
)
from starkware.starknet.core.os import os_utils
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
    CompiledClass,
)

from protostar.starknet import Address
from protostar.cheatable_starknet.controllers.transaction_revert_exception import (
    TransactionRevertException,
)
from protostar.starknet.selector import Selector

from .cheatable_deprecated_syscall_handler import CheatableDeprecatedSysCallHandler
from .cheatable_syscall_handler import CheatableSyscallHandler

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
        class_hash: Optional[int] = None,
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
        syscall_handler = CheatableDeprecatedSysCallHandler(
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
        tx_execution_context: TransactionExecutionContext,
        general_config: StarknetGeneralConfig,
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

    def _execute(
        self,
        state: SyncState,
        compiled_class: CompiledClass,
        class_hash: int,
        resources_manager: ExecutionResourcesManager,
        general_config: StarknetGeneralConfig,
        tx_execution_context: TransactionExecutionContext,
        support_reverted: bool,
    ) -> CallInfo:
        # Fix the current resources usage, in order to calculate the usage of this run at the end.
        previous_cairo_usage = resources_manager.cairo_usage

        # Create a dummy layout.
        layout = dataclasses.replace(
            STARKNET_LAYOUT_INSTANCE,
            builtins={**STARKNET_LAYOUT_INSTANCE.builtins, "segment_arena": {}},
        )

        # Prepare runner.
        entry_point = self._get_selected_entry_point(
            compiled_class=compiled_class, class_hash=class_hash
        )
        program = compiled_class.get_runnable_program(
            entrypoint_builtins=as_non_optional(entry_point.builtins)
        )
        with wrap_with_stark_exception(code=StarknetErrorCode.SECURITY_ERROR):
            runner = CairoFunctionRunner(
                program=program,
                layout=layout,
                additional_builtin_factories=dict(
                    segment_arena=lambda name, included: SegmentArenaBuiltinRunner(  # pyright: ignore
                        included=included
                    )
                ),
            )

        # Prepare implicit arguments.
        implicit_args = os_utils.prepare_os_implicit_args(
            runner=runner, gas=self.initial_gas
        )

        # Prepare syscall handler.
        initial_syscall_ptr = cast(RelocatableValue, implicit_args[-1])
        # region: Modified Starknet Code
        syscall_handler = CheatableSyscallHandler(
            state=state,
            resources_manager=resources_manager,
            segments=runner.segments,
            tx_execution_context=tx_execution_context,
            initial_syscall_ptr=initial_syscall_ptr,
            general_config=general_config,
            entry_point=self,
            support_reverted=support_reverted,
        )
        # endregion

        # Load the builtin costs; Cairo 1.0 programs are expected to end with a `ret` opcode
        # followed by a pointer to the builtin costs.
        core_program_end_ptr = runner.program_base + len(runner.program.data)
        builtin_costs = [0, 0, 0, 0, 0]
        # Use allocate_segment to mark it as read-only.
        builtin_cost_ptr = syscall_handler.allocate_segment(data=builtin_costs)
        program_extra_data: List[MaybeRelocatable] = [
            0x208B7FFF7FFF7FFE,
            builtin_cost_ptr,
        ]
        runner.load_data(ptr=core_program_end_ptr, data=program_extra_data)

        # Arrange all arguments.

        # Allocate and mark the segment as read-only (to mark every input array as read-only).
        calldata_start = syscall_handler.allocate_segment(data=self.calldata)
        calldata_end = calldata_start + len(self.calldata)
        entry_point_args: EntryPointArgs = [
            # Note that unlike old classes, implicit arguments appear flat in the stack.
            *implicit_args,
            calldata_start,
            calldata_end,
        ]

        # Run.
        self._run(
            runner=runner,
            entry_point_offset=entry_point.offset,
            entry_point_args=entry_point_args,
            hint_locals={"syscall_handler": syscall_handler},
            run_resources=tx_execution_context.run_resources,
            program_segment_size=len(runner.program.data) + len(program_extra_data),
            allow_tmp_segments=True,
        )

        # We should not count (possibly) unsued code as holes.
        runner.mark_as_accessed(
            address=core_program_end_ptr, size=len(program_extra_data)
        )

        # Complete validations.
        os_utils.validate_and_process_os_implicit_args(
            runner=runner,
            syscall_handler=syscall_handler,
            initial_implicit_args=implicit_args,
        )

        # Update resources usage (for the bouncer and fee calculation).
        resources_manager.cairo_usage += runner.get_execution_resources()

        # Build and return the call info.
        return self._build_call_info(
            class_hash=class_hash,
            execution_resources=resources_manager.cairo_usage - previous_cairo_usage,
            storage=syscall_handler.storage,
            result=get_call_result(runner=runner, initial_gas=self.initial_gas),
            events=syscall_handler.events,
            l2_to_l1_messages=syscall_handler.l2_to_l1_messages,
            internal_calls=syscall_handler.internal_calls,
        )

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
