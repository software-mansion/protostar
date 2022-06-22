from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.declare_cheatcode import DeclareCheatcode
from protostar.commands.test.cheatcodes.deploy_cheatcode import (
    DeployCheatcode,
    DeployedContract,
)
from protostar.commands.test.cheatcodes.prepare_cheatcode import PrepareCheatcode
from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.utils.data_transformer_facade import DataTransformerFacade

if TYPE_CHECKING:
    from protostar.commands.test.starkware.cheatable_execute_entry_point import (
        CheatableExecuteEntryPoint,
    )
    from protostar.commands.test.starkware.cheatable_state import CheatableCarriedState


class DeployContractCheatcode(Cheatcode):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        execute_entry_point_cls: Type["CheatableExecuteEntryPoint"],
        tx_execution_context: TransactionExecutionContext,
        state: "CheatableCarriedState",
        caller_address: int,
        contract_address: int,
        starknet_storage: BusinessLogicStarknetStorage,
        general_config: CheatableStarknetGeneralConfig,
        initial_syscall_ptr: RelocatableValue,
        data_transformer: DataTransformerFacade,
    ):
        super().__init__(
            execute_entry_point_cls,
            tx_execution_context,
            state,
            caller_address,
            contract_address,
            starknet_storage,
            general_config,
            initial_syscall_ptr,
            data_transformer,
        )
        self._declare_cheatode = DeclareCheatcode(
            execute_entry_point_cls,
            tx_execution_context,
            state,
            caller_address,
            contract_address,
            starknet_storage,
            general_config,
            initial_syscall_ptr,
            data_transformer,
        )
        self._prepare_cheatode = PrepareCheatcode(
            execute_entry_point_cls,
            tx_execution_context,
            state,
            caller_address,
            contract_address,
            starknet_storage,
            general_config,
            initial_syscall_ptr,
            data_transformer,
        )
        self._deploy_cheatode = DeployCheatcode(
            execute_entry_point_cls,
            tx_execution_context,
            state,
            caller_address,
            contract_address,
            starknet_storage,
            general_config,
            initial_syscall_ptr,
            data_transformer,
        )

    @staticmethod
    def name() -> str:
        return "deploy_contract"

    def build(self) -> Callable[..., Any]:
        return self.deploy_contract

    def deploy_contract(
        self,
        contract_path: str,
        constructor_args: Optional[
            Union[
                List[int],
                Dict[
                    DataTransformerFacade.ArgumentName,
                    DataTransformerFacade.SupportedType,
                ],
            ]
        ] = None,
    ) -> DeployedContract:
        declared_contract = self._declare_cheatode.declare(contract_path)
        prepared_contract = self._prepare_cheatode.prepare(
            declared_contract, constructor_args
        )
        return self._deploy_cheatode.deploy_prepared(prepared_contract)
