from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.internal_transaction import (
    InternalInvokeFunction,
)
import asyncio
import functools
import logging
from typing import List, Tuple, cast

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.cairo_pie import ExecutionResources
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.security import SecurityError
from starkware.cairo.lang.vm.utils import ResourcesError
from starkware.cairo.lang.vm.vm_exceptions import (
    HintException,
    VmException,
    VmExceptionBase,
)
from starkware.starknet.business_logic.execution.execute_entry_point_base import (
    ExecuteEntryPointBase,
)
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    CallType,
    TransactionExecutionContext,
)
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.starknet.business_logic.utils import get_return_values
from starkware.starknet.core.os import os_utils, syscall_utils
from starkware.starknet.definitions import fields
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public import abi as starknet_abi
from starkware.starknet.services.api.contract_class import (
    ContractClass,
    ContractEntryPoint,
)
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage
from starkware.starkware_utils.error_handling import (
    StarkException,
    stark_assert,
    wrap_with_stark_exception,
)

from typing import List, Optional, Union

from starkware.python.utils import from_bytes
from starkware.starknet.business_logic.execution.objects import TransactionExecutionInfo
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.services.api.contract_class import ContractClass, EntryPointType
from starkware.starknet.services.api.messages import StarknetMessageToL1
from starkware.starknet.testing.contract import DeclaredClass, StarknetContract
from starkware.starknet.testing.contract_utils import get_abi, get_contract_class
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starknet.testing.state import (
    CastableToAddress,
    CastableToAddressSalt,
    StarknetState,
)

import copy
from typing import Dict, List, Optional, Tuple, Union

from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    Event,
    TransactionExecutionInfo,
)
from starkware.starknet.business_logic.internal_transaction import (
    InternalDeclare,
    InternalDeploy,
    InternalInvokeFunction,
)
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.starknet.definitions import constants, fields
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class import ContractClass, EntryPointType
from starkware.starknet.services.api.messages import StarknetMessageToL1
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext
import dataclasses
import logging
from abc import abstractmethod
from dataclasses import field
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Type

import marshmallow
import marshmallow_dataclass
from marshmallow_oneofschema import OneOfSchema

from services.everest.api.gateway.transaction import EverestTransaction
from services.everest.business_logic.internal_transaction import (
    EverestInternalTransaction,
)
from services.everest.business_logic.state import CarriedStateBase
from starkware.cairo.lang.vm.cairo_pie import ExecutionResources
from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    CallType,
    TransactionExecutionContext,
    TransactionExecutionInfo,
)
from starkware.starknet.business_logic.internal_transaction_interface import (
    InternalStateTransaction,
)
from starkware.starknet.business_logic.state.state import (
    BlockInfo,
    CarriedState,
    StateSelector,
)
from starkware.starknet.business_logic.transaction_fee import (
    calculate_tx_fee,
    execute_fee_transfer,
)
from starkware.starknet.business_logic.utils import (
    preprocess_invoke_function_fields,
    read_contract_class,
    validate_version,
    write_contract_class_fact,
)

from starkware.starknet.core.os.class_hash import compute_class_hash
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.core.os.syscall_utils import initialize_contract_state
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
    calculate_deploy_transaction_hash,
    calculate_transaction_hash_common,
)
from starkware.starknet.definitions import constants, fields
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.definitions.transaction_type import TransactionType
from starkware.starknet.public import abi as starknet_abi
from starkware.starknet.services.api.contract_class import (
    CONSTRUCTOR_SELECTOR,
    ContractClass,
    EntryPointType,
)
from starkware.starknet.services.api.gateway.transaction import (
    DECLARE_SENDER_ADDRESS,
    Declare,
    Deploy,
    InvokeFunction,
    Transaction,
)
from starkware.starkware_utils.config_base import Config
from starkware.starkware_utils.error_handling import stark_assert, stark_assert_eq
from starkware.storage.storage import FactFetchingContext, Storage

# from protostar.commands.test.starkware.cheatable_syscall_handler import CheatableSysCallHandler

# class Contract:
# def __init__(self, contract_path: str, constructor_calldata: Optional[Union[List[int], Dict]] = None):
#
#     self._constructor_calldata = constructor_calldata
#     self._declared = test_env.declare_in_env(self._contract_path)
#     self._deployer_address = 111
#     self._contract_address = self.calculate_contract_address()

# def calculate_contract_address(self):
#     return calculate_contract_address_from_hash(
#         salt=cast(int, nonce),
#         class_hash=self._declared.class_hash,
#         constructor_calldata=self._constructor_calldata,
#         deployer_address=self.contract_address,
#     )


#     @property
#     def class_hash(self) -> int:
#         return self._declared.class_hash

#     @property
#     def contract_address(self) -> AddressType:
#         return self._contract_address


#     def deploy(self):
#         assert not self._deployed # TODO error
#         if isinstance(self._constructor_calldata, Mapping):
#             fn_name = "constructor"
#             constructor_calldata = DataTransformerFacade.from_contract_path(
#                 Path(self._contract_path), starknet_compiler
#             ).from_python(fn_name, **self._constructor_calldata)
#         else:
#             constructor_calldata = self._constructor_calldata
#         test_env.deploy_in_env(self._contract_path, constructor_calldata)


logger = logging.getLogger(__name__)


def contract_build(deployer_address, state, general_config):
    class Contract:
        def __init__(self, contract_path, constructor_calldata=None):
            self._genral_config = general_config
            self._contract_path = contract_path
            self._constructor_calldata = constructor_calldata
            self._deployer_address = deployer_address
            self._state = state
            self._declared = asyncio.run(self._declare_contract())

        async def _declare_contract(self):
            contract_class = get_contract_class(
                source=self._contract_path, cairo_path=[]  # TODO
            )

            tx = await InternalDeclare.create_for_testing(
                ffc=self._state.ffc,
                contract_class=contract_class,
                chain_id=self._genral_config.chain_id.value,
            )

            with self._state.copy_and_apply() as state_copy:
                tx_execution_info = await tx.apply_state_updates(
                    state=state_copy, general_config=self._genral_config
                )

            class_hash = tx_execution_info.call_info.class_hash
            assert class_hash is not None
            return DeclaredClass(
                class_hash=from_bytes(class_hash),
                abi=get_abi(contract_class=contract_class),
            )

        @property
        def contract_address(self):
            pass

        def deploy(self):
            pass

    return Contract


@marshmallow_dataclass.dataclass(frozen=True)
class CheatableInternalInvokeFunction(InternalInvokeFunction):
    async def execute(
        self,
        state: CarriedState,
        general_config: StarknetGeneralConfig,
        only_query: bool = False,
    ) -> CallInfo:
        """
        Builds the transaction execution context and executes the entry point.
        Returns the CallInfo.
        """
        # Sanity check for query mode.
        validate_version(version=self.version, only_query=only_query)

        call = CheatableExecuteEntryPoint(
            call_type=CallType.CALL,
            class_hash=None,
            contract_address=self.contract_address,
            code_address=None,
            entry_point_selector=self.entry_point_selector,
            entry_point_type=self.entry_point_type,
            calldata=self.calldata,
            caller_address=self.caller_address,
        )

        return await call.execute(
            state=state,
            general_config=general_config,
            tx_execution_context=self.get_execution_context(
                n_steps=general_config.invoke_tx_max_n_steps
            ),
        )


class CheatableExecuteEntryPoint(ExecuteEntryPoint):
    def _run(
        self,
        state: CarriedState,
        general_config: StarknetGeneralConfig,
        loop: asyncio.AbstractEventLoop,
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
        class_hash = self._get_class_hash(state=state)
        contract_class = state.get_contract_class(class_hash=class_hash)
        contract_class.validate()

        entry_point = self._get_selected_entry_point(
            contract_class=contract_class, state=state
        )

        # Run the specified contract entry point with given calldata.
        with wrap_with_stark_exception(code=StarknetErrorCode.SECURITY_ERROR):
            runner = CairoFunctionRunner(program=contract_class.program, layout="all")
        os_context = os_utils.prepare_os_context(runner=runner)

        # Extract pre-fetched contract state from carried state.
        pre_run_contract_carried_state = state.contract_states[self.contract_address]
        contract_state = pre_run_contract_carried_state.state
        contract_state.assert_initialized(contract_address=self.contract_address)

        starknet_storage = BusinessLogicStarknetStorage(
            commitment_tree=contract_state.storage_commitment_tree,
            ffc=state.ffc,
            # Pass a copy of the carried storage updates (instead of a reference) - note that
            # pending_modifications may be modified during the run as a result of an internal call.
            pending_modifications=dict(pre_run_contract_carried_state.storage_updates),
            loop=loop,
        )

        initial_syscall_ptr = cast(
            RelocatableValue, os_context[starknet_abi.SYSCALL_PTR_OFFSET]
        )

        # --- PROTOSTAR MODIFICATIONS ---
        # syscall_handler = CheatableSysCallHandler(
        syscall_handler = syscall_utils.BusinessLogicSysCallHandler(
            execute_entry_point_cls=ExecuteEntryPoint,
            tx_execution_context=tx_execution_context,
            state=state,
            caller_address=self.caller_address,
            contract_address=self.contract_address,
            starknet_storage=starknet_storage,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
        )
        contract_cheatcode = contract_build(
            self.contract_address, state, general_config
        )

        # Positional arguments are passed to *args in the 'run_from_entrypoint' function.
        entry_points_args = [
            self.entry_point_selector,
            os_context,
            len(self.calldata),
            self.calldata,
        ]

        try:
            runner.run_from_entrypoint(
                entry_point.offset,
                *entry_points_args,
                hint_locals={
                    "__storage": starknet_storage,
                    "syscall_handler": syscall_handler,
                    "Contract": contract_cheatcode,
                },
                static_locals={
                    "__find_element_max_size": 2**20,
                    "__squash_dict_max_size": 2**20,
                    "__keccak_max_size": 2**20,
                    "__usort_max_size": 2**20,
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

            raise StarkException(code=code, message=str(exception))
        except VmExceptionBase as exception:
            raise StarkException(
                code=StarknetErrorCode.TRANSACTION_FAILED, message=str(exception)
            )
        except SecurityError as exception:
            raise StarkException(
                code=StarknetErrorCode.SECURITY_ERROR, message=str(exception)
            )
        except Exception:
            logger.error("Got an unexpected exception.", exc_info=True)
            raise StarkException(
                code=StarknetErrorCode.UNEXPECTED_FAILURE,
                message="Got an unexpected exception during the execution of the transaction.",
            )

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
