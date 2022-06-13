import asyncio
import logging
from pathlib import Path
import random
from typing import Callable, List, Tuple, cast
from dataclasses import dataclass

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.cairo.lang.vm.security import SecurityError
from starkware.cairo.lang.vm.utils import ResourcesError
from starkware.cairo.lang.vm.vm_exceptions import (
    HintException,
    VmException,
    VmExceptionBase,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.starknet.core.os import os_utils, syscall_utils
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public import abi as starknet_abi
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage
from starkware.starkware_utils.error_handling import (
    StarkException,
    wrap_with_stark_exception,
)

from starkware.python.utils import from_bytes
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import get_abi, get_contract_class
from starkware.python.utils import to_bytes


from starkware.starknet.business_logic.internal_transaction import (
    InternalDeclare,
)
import logging
from starkware.starknet.business_logic.execution.execute_entry_point import (
    ExecuteEntryPoint,
)
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler, initialize_contract_state
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)


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

@dataclass
class DeclaredContract:
    class_hash: int

@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int

@dataclass(frozen=True)
class DeployedContract:
    contract_address: int

class DeploymentManager(BusinessLogicSysCallHandler):
    @property
    def cheatable_state(self):
        return self.state

    def deploy(self, prepared):
        class_hash_bytes = to_bytes(prepared.class_hash)
        future = asyncio.run_coroutine_threadsafe(
            coro=initialize_contract_state(
                state=self.cheatable_state,
                class_hash=class_hash_bytes,
                contract_address=prepared.contract_address,
            ),
            loop=self.loop,
        )
        future.result()


        self.execute_constructor_entry_point(
            contract_address=self.contract_address,
            class_hash_bytes=class_hash_bytes,
            constructor_calldata=prepared.constructor_calldata,
        )
        return DeployedContract(prepared.contract_address)

    def prepare(self, declared, constructor_calldata = None) -> PreparedContract:
        constructor_calldata = constructor_calldata or []
        contract_address: int = calculate_contract_address_from_hash(
            salt=random.randint(0, 10000000000),
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=self.contract_address,
        )
        return PreparedContract(constructor_calldata, contract_address, declared.class_hash)
        

    def declare(self, contract_path) -> DeclaredContract: 
        class_hash = cast(int, asyncio.run(self._declare_contract(contract_path)).class_hash)
        return DeclaredContract(class_hash)

    async def _declare_contract(self, contract_path):
        contract_class = get_contract_class(
            source=contract_path, cairo_path=[]  # TODO
        )

        tx = await InternalDeclare.create_for_testing(
            ffc=self.cheatable_state.ffc,
            contract_class=contract_class,
            chain_id=self.general_config.chain_id.value
        )

        with self.cheatable_state.copy_and_apply() as state_copy:
            tx_execution_info = await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config 
            )

        class_hash = tx_execution_info.call_info.class_hash
        assert class_hash is not None
        return DeclaredClass(
            class_hash=from_bytes(class_hash),
            abi=get_abi(contract_class=contract_class),
        )

def build_deploy_contract(manager) -> Callable[[Path, List[int]], DeployedContract]: #TODO add transformer
    """
    Syntatic sugar for contract deployment compatible with old interface
    """
    def deploy_contract(path: Path, constructor_calldata: List[int]) -> DeployedContract:
        declared = manager.declare("./tests/integration/cheatcodes/deploy_contract_new/basic_contract.cairo")
        prepared = manager.prepare(declared)
        return manager.deploy(prepared)
    return deploy_contract


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

        # --- MODIFICATIONS START ---
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

        deployment_manager = DeploymentManager(
            execute_entry_point_cls=ExecuteEntryPoint,
            tx_execution_context=tx_execution_context,
            state=state,
            caller_address=self.caller_address,
            contract_address=self.contract_address,
            starknet_storage=starknet_storage,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
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
                hint_locals= {
                    "__storage": starknet_storage,
                    "syscall_handler": syscall_handler,
                    "declare": deployment_manager.declare,
                    "prepare": deployment_manager.prepare,
                    "deploy": deployment_manager.deploy,
                    "deploy_contract": build_deploy_contract(deployment_manager)
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
