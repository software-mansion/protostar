import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, cast

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.debug_info import DebugInfo
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.memory_dict import MemoryDict
from starkware.cairo.lang.vm.memory_segments import FIRST_MEMORY_ADDR as PROGRAM_BASE
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.security import SecurityError
from starkware.cairo.lang.vm.trace_entry import TraceEntry
from starkware.cairo.lang.vm.utils import ResourcesError
from starkware.cairo.lang.vm.vm_exceptions import (
    HintException,
    VmException,
    VmExceptionBase,
)
from starkware.python.utils import from_bytes
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.business_logic.utils import validate_contract_deployed
from starkware.starknet.core.os import os_utils, syscall_utils
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public import abi as starknet_abi
from starkware.starknet.services.api.contract_class import (
    ContractClass,
    ContractEntryPoint,
)
from starkware.starkware_utils.error_handling import (
    StarkException,
    wrap_with_stark_exception,
)

from protostar.profiler.contract_profiler import (
    RuntimeProfile,
    TracerDataManager,
    build_profile,
)
from protostar.profiler.pprof import serialize, to_protobuf
from protostar.profiler.transaction_profiler import merge_profiles
from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.cheatable_cairo_function_runner import (
    CheatableCairoFunctionRunner,
)
from protostar.starknet.cheatable_syscall_handler import CheatableSysCallHandler
from protostar.starknet.cheatcode import Cheatcode

if TYPE_CHECKING:
    from protostar.starknet.cheatcode_factory import CheatcodeFactory

logger = logging.getLogger(__name__)


ContractFilename = str


@dataclass(frozen=True)
class ContractProfile:
    contract_callstack: list[ContractFilename]
    entry_point: ContractEntryPoint
    profile: RuntimeProfile


# TODO(mkaput): Eradicate this function in favor of `cheaters`.
def extract_cheatable_state(state: SyncState) -> CheatableCachedState:
    assert isinstance(state, StateSyncifier)
    async_state = state.async_state
    assert isinstance(async_state, CheatableCachedState)
    return async_state


# pylint: disable=raise-missing-from
# pylint: disable=too-many-statements
# TODO(maksymiliandemitraszek): Enable it again
# pylint: disable=too-many-branches
class CheatableExecuteEntryPoint(ExecuteEntryPoint):
    cheatcode_factory: Optional["CheatcodeFactory"] = None
    samples: list[ContractProfile] = []
    contract_callstack: list[str] = []
    profiling = False

    def _run(
        self,
        state: SyncState,
        resources_manager: ExecutionResourcesManager,
        general_config: StarknetGeneralConfig,
        tx_execution_context: TransactionExecutionContext,
    ) -> Tuple[CairoFunctionRunner, syscall_utils.BusinessLogicSysCallHandler]:
        """
        Runs the selected entry point with the given calldata in the code of the contract deployed
        at self.code_address.
        The execution is done in the context (e.g., storage) of the contract at
        self.contract_address.
        Returns the corresponding CairoFunctionRunner and BusinessLogicSysCallHandler in order to
        retrieve the execution information.
        """
        # Prepare input for Cairo function runner.
        class_hash = self._get_code_class_hash(state=state)
        contract_class = state.get_contract_class(class_hash=class_hash)
        contract_class.validate()

        entry_point = self._get_selected_entry_point(
            contract_class=contract_class, class_hash=class_hash
        )

        # Run the specified contract entry point with given calldata.
        with wrap_with_stark_exception(code=StarknetErrorCode.SECURITY_ERROR):
            # region Modified Starknet code.
            runner = CheatableCairoFunctionRunner(
                program=contract_class.program, layout="all"
            )
            # endregion

        os_context = os_utils.prepare_os_context(runner=runner)

        validate_contract_deployed(state=state, contract_address=self.contract_address)

        initial_syscall_ptr = cast(
            RelocatableValue, os_context[starknet_abi.SYSCALL_PTR_OFFSET]
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
            )
        )
        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

        for custom_hint_local in cheatcode_factory.build_hint_locals():
            hint_locals[custom_hint_local.name] = custom_hint_local.build()

        # endregion

        # Positional arguments are passed to *args in the 'run_from_entrypoint' function.
        entry_points_args = [
            self.entry_point_selector,
            os_context,
            len(self.calldata),
            # Allocate and mark the segment as read-only (to mark every input array as read-only).
            # pylint: disable=protected-access
            syscall_handler._allocate_segment(
                segments=runner.segments, data=self.calldata
            ),
        ]

        # region Modified Starknet code.
        if self.profiling:
            self.append_contract_callstack(state, class_hash)
        # endregion

        try:
            runner.run_from_entrypoint(
                entry_point.offset,
                *entry_points_args,
                # region Modified Starknet code.
                hint_locals={
                    **hint_locals,
                    "syscall_handler": syscall_handler,
                },
                # endregion
                static_locals={
                    "__find_element_max_size": 2**20,
                    "__squash_dict_max_size": 2**20,
                    "__keccak_max_size": 2**20,
                    "__usort_max_size": 2**20,
                    "__chained_ec_op_max_len": 1000,
                },
                run_resources=tx_execution_context.run_resources,
                verify_secure=True,
            )

        except VmException as exception:
            code = StarknetErrorCode.TRANSACTION_FAILED
            if isinstance(exception.inner_exc, HintException):
                hint_exception = exception.inner_exc

                if isinstance(hint_exception.inner_exc, syscall_utils.HandlerException):
                    stark_exception = hint_exception.inner_exc.stark_exception
                    code = stark_exception.code
                    called_contract_address = (
                        hint_exception.inner_exc.called_contract_address
                    )
                    message_prefix = f"Error in the called contract ({hex(called_contract_address)}):\n"
                    # Override python's traceback and keep the Cairo one of the inner exception.
                    exception.notes = [message_prefix + str(stark_exception.message)]

            if isinstance(exception.inner_exc, ResourcesError):
                code = StarknetErrorCode.OUT_OF_RESOURCES

            raise StarkException(code=code, message=str(exception)) from exception
        except VmExceptionBase as exception:
            raise StarkException(
                code=StarknetErrorCode.TRANSACTION_FAILED, message=str(exception)
            ) from exception
        except SecurityError as exception:
            raise StarkException(
                code=StarknetErrorCode.SECURITY_ERROR, message=str(exception)
            ) from exception
        except Exception as exception:
            logger.error("Got an unexpected exception.", exc_info=True)
            raise StarkException(
                code=StarknetErrorCode.UNEXPECTED_FAILURE,
                message="Got an unexpected exception during the execution of the transaction.",
            ) from exception

        # Complete handler validations.
        os_utils.validate_and_process_os_context(
            runner=runner,
            syscall_handler=syscall_handler,
            initial_os_context=os_context,
        )

        # When execution starts the stack holds entry_points_args + [ret_fp, ret_pc].
        args_ptr = runner.initial_fp - (len(entry_points_args) + 2)

        # The arguments are touched by the OS and should not be counted as holes, mark them
        # as accessed.
        assert isinstance(args_ptr, RelocatableValue)  # Downcast.
        runner.mark_as_accessed(address=args_ptr, size=len(entry_points_args))

        # region Modified Starknet code.

        if self.profiling:
            self.append_runtime_profile(runner, contract_class, entry_point)
            self.pop_contract_callstack()
            if not CheatableExecuteEntryPoint.contract_callstack:
                merge_and_save(CheatableExecuteEntryPoint.samples)

        # endregion

        return runner, syscall_handler

    def append_contract_callstack(self, state: SyncState, class_hash: bytes):
        if not CheatableExecuteEntryPoint.contract_callstack:
            CheatableExecuteEntryPoint.contract_callstack.append("TEST_CONTRACT")
        else:
            path = extract_cheatable_state(state).class_hash_to_contract_path_map[
                from_bytes(class_hash)
            ]
            CheatableExecuteEntryPoint.contract_callstack.append(str(path))

    def pop_contract_callstack(self):
        CheatableExecuteEntryPoint.contract_callstack.pop()

    def append_runtime_profile(
        self,
        runner: CairoFunctionRunner,
        contract_class: ContractClass,
        entry_point: ContractEntryPoint,
    ):
        runner.relocate()
        profile = get_profile(
            program=contract_class.program,
            memory=runner.relocated_memory,
            trace=runner.relocated_trace,
            debug_info=runner.get_relocated_debug_info(),
            runner=runner,
        )
        current_callstack = CheatableExecuteEntryPoint.contract_callstack.copy()
        CheatableExecuteEntryPoint.samples.append(
            ContractProfile(current_callstack, entry_point, profile)
        )


def get_profile(
    program: Program,
    memory: MemoryDict,
    trace: List[TraceEntry[int]],
    debug_info: DebugInfo,
    runner: CairoFunctionRunner,
):
    tracer_data = TracerDataManager(
        program=program,
        memory=memory,
        trace=trace,
        program_base=PROGRAM_BASE,
        air_public_input=None,
        debug_info=debug_info,
    )
    assert runner.accessed_addresses
    assert runner.segment_offsets
    profile = build_profile(
        tracer_data,
        runner.segments,
        runner.segment_offsets,
        runner.accessed_addresses,
        runner.builtin_runners,  # type: ignore
    )
    return profile


def merge_and_save(contract_samples: list[ContractProfile]):
    merged = merge_profiles(contract_samples)
    proto = to_protobuf(merged)
    serialized = serialize(proto)
    Path("profile.pb.gz").write_bytes(serialized)
