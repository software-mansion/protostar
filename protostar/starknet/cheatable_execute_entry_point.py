import asyncio
from dataclasses import dataclass
import logging
from pathlib import Path
from subprocess import call
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, cast
import logging
from typing import TYPE_CHECKING, Optional, Tuple, cast, Any

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.security import SecurityError
from starkware.cairo.lang.vm.utils import ResourcesError
from starkware.cairo.lang.vm.vm_exceptions import (
    HintException,
    VmException,
    VmExceptionBase,
)
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.business_logic.utils import validate_contract_deployed
from starkware.starknet.core.os import os_utils, syscall_utils
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public import abi as starknet_abi
from starkware.starkware_utils.error_handling import (
    StarkException,
    wrap_with_stark_exception,
)
from starkware.cairo.lang.tracer.tracer_data import TracerData
from starkware.cairo.lang.vm.memory_segments import FIRST_MEMORY_ADDR as PROGRAM_BASE
from starkware.starknet.services.api.contract_class import ContractEntryPoint
from starkware.python.utils import from_bytes
from protostar.profiler.pprof import serialize, to_protobuf
from protostar.profiler.profile import RuntimeProfile, build_profile, merge_profiles, profile_from_tracer_data
from protostar.profiler.profile import profile_from_tracer_data

from protostar.starknet.cheatable_cairo_function_runner import (
    CheatableCairoFunctionRunner,
)
from protostar.starknet.cheatable_syscall_handler import CheatableSysCallHandler
from protostar.starknet.cheatcode import Cheatcode

PROFILER = False

if TYPE_CHECKING:
    from protostar.starknet.cheatcode_factory import CheatcodeFactory

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ContractProfile:
    callstack: List[str]
    entry_point: ContractEntryPoint
    profile: RuntimeProfile


# pylint: disable=raise-missing-from
# pylint: disable=too-many-statements
class CheatableExecuteEntryPoint(ExecuteEntryPoint):
    cheatcode_factory: Optional["CheatcodeFactory"] = None
    samples: List[ContractProfile] = []
    callstack: List[str] = []

    def _run(  # type: ignore
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
        syscall_dependencies = Cheatcode.SyscallDependencies(
            execute_entry_point_cls=CheatableExecuteEntryPoint,
            tx_execution_context=tx_execution_context,
            state=state,
            resources_manager=resources_manager,
            caller_address=self.caller_address,
            contract_address=self.contract_address,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
        )

        syscall_handler = CheatableSysCallHandler(**syscall_dependencies)

        hint_locals: dict[str, Any] = {}

        cheatcode_factory = CheatableExecuteEntryPoint.cheatcode_factory
        assert (
            cheatcode_factory is not None
        ), "Tried to use CheatableExecuteEntryPoint without cheatcodes."

        cheatcodes = cheatcode_factory.build_cheatcodes(
            syscall_dependencies=syscall_dependencies,
            internal_calls=syscall_handler.internal_calls,
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

        try:
            if PROFILER:
                if  CheatableExecuteEntryPoint.callstack == []:
                    CheatableExecuteEntryPoint.callstack.append("MAIN")
                else:
                    path = state.class_hash_to_contract_path[from_bytes(class_hash)]
                    CheatableExecuteEntryPoint.callstack.append(path)

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
            if PROFILER:
                runner.relocate()
                try:
                    profile = get_profile(
                        program=contract_class.program,
                        memory=runner.relocated_memory,
                        trace=runner.relocated_trace,
                        debug_info=runner.get_relocated_debug_info(),
                        runner=runner,
                    )
                    current_callstack = CheatableExecuteEntryPoint.callstack.copy()
                    CheatableExecuteEntryPoint.samples.append(ContractProfile(current_callstack, entry_point, profile))
                    CheatableExecuteEntryPoint.callstack.pop()
                    if CheatableExecuteEntryPoint.callstack == []:
                        merge_and_save(CheatableExecuteEntryPoint.samples)

                except Exception as err:                
                    import traceback
                    import sys
                    print(str(err))
                    raise err

        # --- MODIFICATIONS END ---

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

        return runner, syscall_handler


def get_profile(program, memory, trace, debug_info, runner):
    tracer_data = TracerData(
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
        tracer_data, runner.segments, runner.segment_offsets, runner.accessed_addresses
    )
    return profile

def merge_and_save(contract_samples: List[ContractProfile]):
    merged = merge_profiles(contract_samples)
    proto = to_protobuf(merged)
    serialized = serialize(proto)
    with open("profile.pb.gz", "wb") as file:
        file.write(serialized)
    return 0
