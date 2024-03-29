# pylint: disable=protected-access
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, cast
from copy import deepcopy

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.relocatable import RelocatableValue

from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
    EntryPointArgs,
)
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    TransactionExecutionContext,
    ExecutionResourcesManager,
)
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import State, SyncState
from starkware.starknet.business_logic.utils import (
    get_call_result_for_version0_class,
)
from starkware.starknet.core.os import os_utils
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import (
    StarknetGeneralConfig,
    STARKNET_LAYOUT_INSTANCE,
)
from starkware.starknet.public import abi as starknet_abi
from starkware.starknet.services.api.contract_class.contract_class import (
    DeprecatedCompiledClass,
)
from starkware.starkware_utils.error_handling import (
    wrap_with_stark_exception,
)

from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.cheatable_syscall_handler import CheatableSysCallHandler
from protostar.starknet.cheatcode import Cheatcode

if TYPE_CHECKING:
    from protostar.starknet.cheatcode_factory import CheatcodeFactory

logger = logging.getLogger(__name__)


ContractFilename = str

FAULTY_CLASS_HASH = to_bytes(
    0x1A7820094FEAF82D53F53F214B81292D717E7BB9A92BB2488092CD306F3993F
)


@dataclass(frozen=True)
class ContractProfile:
    contract_callstack: list[ContractFilename]


def extract_cheatable_state(state: SyncState) -> CheatableCachedState:
    assert isinstance(state, StateSyncifier)
    async_state = state.async_state
    assert isinstance(async_state, CheatableCachedState)
    return async_state


# pylint: disable=raise-missing-from
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
class CheatableExecuteEntryPoint(ExecuteEntryPoint):
    cheatcode_factory: Optional["CheatcodeFactory"] = None
    samples: list[ContractProfile] = []
    contract_callstack: list[str] = []

    max_steps: Optional[int] = None
    "``None`` means default Cairo value."

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

        hint_locals: dict[str, Any] = {}

        cheatcode_factory = CheatableExecuteEntryPoint.cheatcode_factory
        assert (
            cheatcode_factory is not None
        ), "Tried to use CheatableExecuteEntryPoint without cheatcodes."

        cheatcodes = cheatcode_factory.build_cheatcodes(
            syscall_dependencies=Cheatcode.SyscallDependencies(
                execute_entry_point_cls=CheatableExecuteEntryPoint,
                tx_execution_context=tx_execution_context,
                state=state,
                resources_manager=resources_manager,
                caller_address=self.caller_address,
                contract_address=self.contract_address,
                general_config=general_config,
                initial_syscall_ptr=initial_syscall_ptr,
                shared_internal_calls=syscall_handler.internal_calls,
                segments=runner.segments,
            )
        )
        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

        for custom_hint_local in cheatcode_factory.build_hint_locals():
            hint_locals[custom_hint_local.name] = custom_hint_local.build()

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
            hint_locals={
                "syscall_handler": syscall_handler,
                **hint_locals,
            },
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

    def append_contract_callstack(self, state: SyncState, class_hash: int):
        if not CheatableExecuteEntryPoint.contract_callstack:
            CheatableExecuteEntryPoint.contract_callstack.append("TEST_CONTRACT")
        else:
            path = extract_cheatable_state(state).class_hash_to_contract_path_map[
                class_hash
            ]
            CheatableExecuteEntryPoint.contract_callstack.append(str(path))

    def pop_contract_callstack(self):
        CheatableExecuteEntryPoint.contract_callstack.pop()

    async def execute_for_testing(
        self,
        state: State,
        general_config: StarknetGeneralConfig,
        resources_manager: Optional[ExecutionResourcesManager] = None,
        tx_execution_context: Optional[TransactionExecutionContext] = None,
    ) -> CallInfo:
        new_config = deepcopy(general_config)
        if self.max_steps is not None:
            # Providing a negative value to Protostar results in infinite steps,
            # this is here to mimic default Cairo behavior
            value = None if self.max_steps < 0 else self.max_steps

            # NOTE: We are doing it this way to avoid TypeError from typeguard
            new_config.__dict__["invoke_tx_max_n_steps"] = value

        return await super().execute_for_testing(
            state, new_config, resources_manager, tx_execution_context
        )
