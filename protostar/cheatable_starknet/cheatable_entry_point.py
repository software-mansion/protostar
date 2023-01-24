# pylint: disable=duplicate-code
import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple, cast, List, TYPE_CHECKING, Any
from copy import deepcopy

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
)
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    TransactionExecutionContext,
    CallType,
)
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import State, SyncState
from starkware.starknet.business_logic.utils import validate_contract_deployed
from starkware.starknet.core.os import os_utils, syscall_utils
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public import abi as starknet_abi
from starkware.starknet.services.api.contract_class import EntryPointType
from starkware.starkware_utils.error_handling import (
    StarkException,
    wrap_with_stark_exception,
)

from protostar.cheatable_starknet.cheaters.transaction_revert_exception import (
    TransactionRevertException,
)

from .cheatable_syscall_handler import CheatableSysCallHandler

if TYPE_CHECKING:
    from .cheaters import CairoCheaters

FAULTY_CLASS_HASH = to_bytes(
    0x1A7820094FEAF82D53F53F214B81292D717E7BB9A92BB2488092CD306F3993F
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CheatableExecuteEntryPoint(ExecuteEntryPoint):
    cheaters: "CairoCheaters"
    max_steps: Optional[int] = None
    "``None`` means default Cairo value."

    @classmethod
    def create_with_cheaters(
        cls,
        contract_address: int,
        calldata: List[int],
        entry_point_selector: int,
        cheaters: "CairoCheaters",
    ) -> "CheatableExecuteEntryPoint":
        return cls(
            entry_point_selector=entry_point_selector,
            calldata=calldata,
            contract_address=contract_address,
            cheaters=cheaters,
            code_address=None,
            class_hash=None,
            call_type=CallType.CALL,
            entry_point_type=EntryPointType.EXTERNAL,
            caller_address=0,
        )

    @classmethod
    def factory(cls, cheaters: "CairoCheaters") -> type[ExecuteEntryPoint]:
        def factory_function(*args: Any, **kwargs: Any) -> ExecuteEntryPoint:
            return cls(*args, cheaters=cheaters, **kwargs)

        return cast(type[ExecuteEntryPoint], factory_function)

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

        # Hack to prevent version 0 attack on argent accounts.
        if (tx_execution_context.version == 0) and (class_hash == FAULTY_CLASS_HASH):
            raise StarkException(
                code=StarknetErrorCode.TRANSACTION_FAILED,
                message="Fraud attempt blocked.",
            )

        contract_class = state.get_contract_class(class_hash=class_hash)
        contract_class.validate()

        entry_point = self._get_selected_entry_point(
            contract_class=contract_class, class_hash=class_hash
        )

        # Run the specified contract entry point with given calldata.
        with wrap_with_stark_exception(code=StarknetErrorCode.SECURITY_ERROR):
            runner = CairoFunctionRunner(program=contract_class.program, layout="all")

        os_context = os_utils.prepare_os_context(runner=runner)

        validate_contract_deployed(state=state, contract_address=self.contract_address)

        initial_syscall_ptr = cast(
            RelocatableValue, os_context[starknet_abi.SYSCALL_PTR_OFFSET]
        )

        # region Modified Starknet code.
        assert isinstance(
            state, StateSyncifier
        ), "Sync state is not a state syncifier!"  # This should always be true
        syscall_handler = CheatableSysCallHandler(
            execute_entry_point_cls=CheatableExecuteEntryPoint.factory(
                cheaters=self.cheaters,
            ),
            tx_execution_context=tx_execution_context,
            state=state,
            resources_manager=resources_manager,
            caller_address=self.caller_address,
            contract_address=self.contract_address,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
        )
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
            runner.run_from_entrypoint(
                entry_point.offset,
                *entry_points_args,
                # region Modified Starknet code.
                hint_locals={
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

        return runner, syscall_handler

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

    def execute(
        self,
        state: SyncState,
        resources_manager: ExecutionResourcesManager,
        general_config: StarknetGeneralConfig,
        tx_execution_context: TransactionExecutionContext,
    ):
        try:
            return super().execute(
                state,
                resources_manager,
                self._change_max_steps_in_general_config(general_config),
                tx_execution_context,
            )
        except StarkException as ex:
            raise self._wrap_stark_exception(ex)

    def _wrap_stark_exception(self, stark_exception: StarkException):
        # This code is going change once Starknet is integrated with Cairo 1.
        message = stark_exception.message or ""
        results = re.findall("Error message: (.*)", message)
        if len(results) > 0:
            message = results[0]
        return TransactionRevertException(message=message, raw_ex=stark_exception)
