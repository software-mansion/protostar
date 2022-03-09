import asyncio
from typing import List, Tuple

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.business_logic.internal_transaction import (
    InternalDeploy,
    InternalInvokeFunction,
)
from starkware.starknet.business_logic.state import CarriedState
from starkware.starknet.business_logic.transaction_execution_objects import (
    ContractCall,
    TransactionExecutionContext,
    TransactionExecutionInfo,
)
from starkware.starknet.core.os import syscall_utils
from starkware.starknet.definitions.error_codes import StarknetErrorCode
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_definition import (
    ContractDefinition,
    EntryPointType,
)
from starkware.starknet.services.api.gateway.contract_address import (
    calculate_contract_address,
)
from starkware.starknet.services.api.gateway.transaction import (
    Deploy,
    InvokeFunction,
    Transaction,
)
from starkware.starknet.services.api.gateway.transaction_hash import (
    calculate_deploy_transaction_hash,
)
from starkware.starkware_utils.error_handling import stark_assert


class CheatableInternalInvokeFunction(InternalInvokeFunction):
    @classmethod
    def _specific_from_external(
        cls, external_tx: Transaction, general_config: StarknetGeneralConfig
    ) -> "CheatableInternalInvokeFunction":
        assert isinstance(external_tx, InvokeFunction)
        return cls.create(
            general_config=general_config,
            contract_address=external_tx.contract_address,
            entry_point_selector=external_tx.entry_point_selector,
            entry_point_type=EntryPointType.EXTERNAL,
            calldata=external_tx.calldata,
            signature=external_tx.signature,
            nonce=None,
        )

    def _run(
        self,
        state: CarriedState,
        general_config: StarknetGeneralConfig,
        loop: asyncio.AbstractEventLoop,
        caller_address: int,
        tx_execution_context: TransactionExecutionContext,
    ) -> Tuple[CairoFunctionRunner, syscall_utils.BusinessLogicSysCallHandler]:
        raise BaseException("test")


class CheatableInternalDeploy(InternalDeploy):
    async def invoke_constructor(
        self, state: CarriedState, general_config: StarknetGeneralConfig
    ) -> TransactionExecutionInfo:
        if (
            len(
                self.contract_definition.entry_points_by_type[
                    EntryPointType.CONSTRUCTOR
                ]
            )
            == 0
        ):
            stark_assert(
                len(self.constructor_calldata) == 0,
                code=StarknetErrorCode.TRANSACTION_FAILED,
                message="Cannot pass calldata to a contract with no constructor.",
            )
            return TransactionExecutionInfo.create(
                call_info=ContractCall.empty(to_address=self.contract_address)
            )

        tx = CheatableInternalInvokeFunction(
            contract_address=self.contract_address,
            code_address=self.contract_address,
            entry_point_selector=get_selector_from_name("constructor"),
            entry_point_type=EntryPointType.CONSTRUCTOR,
            calldata=self.constructor_calldata,
            signature=[],
            hash_value=0,
            caller_address=0,
        )

        return await tx._apply_specific_state_updates(
            state=state, general_config=general_config
        )

    @classmethod
    def _specific_from_external(
        cls, external_tx: Transaction, general_config: StarknetGeneralConfig
    ) -> "CheatableInternalDeploy":
        assert isinstance(external_tx, Deploy)
        return cls.create(
            contract_address_salt=external_tx.contract_address_salt,
            contract_definition=external_tx.contract_definition,
            constructor_calldata=external_tx.constructor_calldata,
            general_config=general_config,
        )

    @classmethod
    def create(
        cls,
        contract_address_salt: int,
        contract_definition: ContractDefinition,
        constructor_calldata: List[int],
        general_config,
    ):
        contract_address = calculate_contract_address(
            salt=contract_address_salt,
            contract_definition=contract_definition,
            constructor_calldata=constructor_calldata,
            caller_address=0,
        )
        return cls(
            contract_address=contract_address,
            contract_address_salt=contract_address_salt,
            contract_definition=contract_definition,
            constructor_calldata=constructor_calldata,
            hash_value=calculate_deploy_transaction_hash(
                contract_address=contract_address,
                constructor_calldata=constructor_calldata,
                chain_id=general_config.chain_id.value,
            ),
        )
