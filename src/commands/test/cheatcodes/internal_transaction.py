import asyncio
from typing import List, Tuple

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.business_logic.internal_transaction import (
    InternalDeploy,
    InternalInvokeFunction,
)
from starkware.starknet.business_logic.state import CarriedState
from starkware.starknet.business_logic.transaction_execution_objects import (
    TransactionExecutionContext,
    TransactionExecutionInfo,
)
from starkware.starknet.core.os import syscall_utils
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.gateway.contract_address import (
    calculate_contract_address,
)
from starkware.starknet.services.api.gateway.transaction import Deploy, Transaction
from starkware.starknet.services.api.gateway.transaction_hash import (
    calculate_deploy_transaction_hash,
)


class CheatableInternalInvokeFunction(InternalInvokeFunction):
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
        raise BaseException("test")

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

    @classmethod
    def _specific_from_external(
        cls, external_tx: Transaction, general_config: StarknetGeneralConfig
    ) -> "InternalDeploy":
        assert isinstance(external_tx, Deploy)
        return cls.create(
            contract_address_salt=external_tx.contract_address_salt,
            contract_definition=external_tx.contract_definition,
            constructor_calldata=external_tx.constructor_calldata,
            general_config=general_config,
        )
