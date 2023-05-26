from typing import Union, List, Optional, cast, Tuple

import marshmallow_dataclass
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    ExecutionResourcesManager,
)
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.business_logic.transaction.objects import InternalInvokeFunction
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class.contract_class import EntryPointType
from starkware.starknet.testing.state import CastableToAddress

from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint


# pylint: disable=too-many-ancestors
@marshmallow_dataclass.dataclass(frozen=True)  # pyright: ignore
class CheatableInternalInvokeFunction(InternalInvokeFunction):
    def run_execute_entrypoint(
        self,
        remaining_gas: int,
        state: SyncState,
        resources_manager: ExecutionResourcesManager,
        general_config: StarknetGeneralConfig,
    ) -> Tuple[CallInfo, int]:
        call = CheatableExecuteEntryPoint.create(
            contract_address=self.sender_address,
            entry_point_selector=self.entry_point_selector,
            entry_point_type=EntryPointType.EXTERNAL,
            calldata=self.calldata,
            caller_address=0,
            initial_gas=remaining_gas,
        )

        call_info = call.execute(
            state=state,
            resources_manager=resources_manager,
            general_config=general_config,
            tx_execution_context=self.get_execution_context(
                n_steps=general_config.invoke_tx_max_n_steps
            ),
        )
        remaining_gas -= call_info.gas_consumed

        return call_info, remaining_gas


async def create_cheatable_invoke_function(
    state: CheatableCachedState,
    contract_address: CastableToAddress,
    selector: Union[int, str],
    calldata: List[int],
    max_fee: int,
    version: int,
    signature: Optional[List[int]],
    nonce: Optional[int],
    chain_id: int,
) -> CheatableInternalInvokeFunction:
    if isinstance(contract_address, str):
        contract_address = int(contract_address, 16)
    assert isinstance(contract_address, int)

    if isinstance(selector, str):
        selector = get_selector_from_name(selector)
    assert isinstance(selector, int)

    if signature is None:
        signature = []

    # We allow not specifying nonce. In this case, the current nonce of the contract will be used.
    if nonce is None:
        nonce = await state.get_nonce_at(contract_address=contract_address)

    return cast(
        CheatableInternalInvokeFunction,
        CheatableInternalInvokeFunction.create(
            sender_address=contract_address,
            entry_point_selector=selector,
            calldata=calldata,
            max_fee=max_fee,
            signature=signature,
            nonce=nonce,
            chain_id=chain_id,
            version=version,
        ),
    )
