from pathlib import Path
from typing import Dict, List, Optional, Union, cast

import marshmallow_dataclass
from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    CallType,
    TransactionExecutionInfo,
)
from starkware.starknet.business_logic.internal_transaction import (
    InternalInvokeFunction,
)
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.starknet.business_logic.utils import validate_version
from starkware.starknet.definitions import constants
from starkware.starknet.public.abi import AbiType, get_selector_from_name
from starkware.starknet.services.api.contract_class import EntryPointType
from starkware.starknet.services.api.messages import StarknetMessageToL1
from starkware.starknet.testing.state import StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext

from protostar.commands.test.starkware.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.commands.test.starkware.types import (
    AddressType,
    ClassHashType,
    SelectorType,
)

CastableToAddress = Union[str, int]
CastableToAddressSalt = Union[str, int]

# pylint: disable=too-many-arguments
# pylint: disable=too-many-ancestors
@marshmallow_dataclass.dataclass(frozen=True)
class CheatableInternalInvokeFunction(InternalInvokeFunction):
    async def execute(
        self,
        state: CarriedState,
        general_config: CheatableStarknetGeneralConfig,
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


def create_cheatable_invoke_function(
    contract_address: CastableToAddress,
    selector: Union[int, str],
    calldata: List[int],
    caller_address: int,
    max_fee: int,
    version: int,
    signature: Optional[List[int]],
    entry_point_type: EntryPointType,
    nonce: Optional[int],
    chain_id: int,
    only_query: bool = False,
) -> CheatableInternalInvokeFunction:

    if isinstance(contract_address, str):
        contract_address = int(contract_address, 16)
    assert isinstance(contract_address, int)

    if isinstance(selector, str):
        selector = get_selector_from_name(selector)
    assert isinstance(selector, int)

    signature = [] if signature is None else signature

    return cast(
        CheatableInternalInvokeFunction,
        CheatableInternalInvokeFunction.create(
            contract_address=contract_address,
            entry_point_selector=selector,
            entry_point_type=entry_point_type,
            calldata=calldata,
            max_fee=max_fee,
            signature=signature,
            caller_address=caller_address,
            nonce=nonce,
            chain_id=chain_id,
            version=version,
            only_query=only_query,
        ),
    )


# pylint: disable=too-many-instance-attributes
class CheatableCarriedState(CarriedState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pranked_contracts_map: Dict[int, int] = {}
        self.mocked_calls_map: Dict[AddressType, Dict[SelectorType, List[int]]] = {}
        self.event_selector_to_name_map: Dict[int, str] = {}
        self.event_name_to_contract_abi_map: Dict[str, AbiType] = {}
        self.class_hash_to_contract_path_map: Dict[ClassHashType, Path] = {}
        self.contract_address_to_class_hash_map: Dict[AddressType, ClassHashType] = {}
        self.contract_address_to_block_timestamp: Dict[AddressType, int] = {}
        self.contract_address_to_block_number: Dict[AddressType, int] = {}

    def _apply(self):
        """Merge state changes with the `self.parent_state`"""
        assert self.parent_state is not None

        self.parent_state.pranked_contracts_map = {
            **self.parent_state.pranked_contracts_map,
            **self.pranked_contracts_map,
        }

        self.parent_state.mocked_calls_map = {**self.parent_state.mocked_calls_map}

        # pylint: disable=consider-using-dict-items
        for address in self.mocked_calls_map:
            if address in self.parent_state.mocked_calls_map:
                self.parent_state.mocked_calls_map[address] = {
                    **self.parent_state.mocked_calls_map[address],
                    **self.mocked_calls_map[address],
                }
            else:
                self.parent_state.mocked_calls_map[address] = self.mocked_calls_map[
                    address
                ]

        self.parent_state.event_selector_to_name_map = {
            **self.parent_state.event_selector_to_name_map,
            **self.event_selector_to_name_map,
        }

        self.parent_state.event_name_to_contract_abi_map = {
            **self.parent_state.event_name_to_contract_abi_map,
            **self.event_name_to_contract_abi_map,
        }

        self.parent_state.class_hash_to_contract_path_map = {
            **self.parent_state.class_hash_to_contract_path_map,
            **self.class_hash_to_contract_path_map,
        }
        self.parent_state.contract_address_to_class_hash_map = {
            **self.parent_state.contract_address_to_class_hash_map,
            **self.contract_address_to_class_hash_map,
        }

        self.parent_state.contract_address_to_block_timestamp = {
            **self.parent_state.contract_address_to_block_timestamp,
            **self.contract_address_to_block_timestamp,
        }

        self.parent_state.contract_address_to_block_number = {
            **self.parent_state.contract_address_to_block_number,
            **self.contract_address_to_block_number,
        }

        return super()._apply()

    def update_event_selector_to_name_map(
        self, local_event_selector_to_name_map: Dict[int, str]
    ):
        for selector, name in local_event_selector_to_name_map.items():
            self.event_selector_to_name_map[selector] = name


class CheatableStarknetState(StarknetState):
    """
    Modified version of StarknetState from testing framework.
    It uses extended version of CarriedState - CheatableCarriedState.
    """

    def __init__(
        self,
        state: CheatableCarriedState,
        general_config: CheatableStarknetGeneralConfig,
    ):
        super().__init__(state, general_config)

    @property
    def cheatable_carried_state(self):
        return cast(CheatableCarriedState, self.state)

    async def invoke_raw(
        self,
        contract_address: CastableToAddress,
        selector: Union[int, str],
        calldata: List[int],
        caller_address: int,
        max_fee: int,
        signature: Optional[List[int]] = None,
        entry_point_type: EntryPointType = EntryPointType.EXTERNAL,
        nonce: Optional[int] = None,
    ) -> TransactionExecutionInfo:
        """
        Invokes a contract function. Returns the execution info.

        Args:
        contract_address - a hexadecimal string or an integer representing the contract address.
        selector - either a function name or an integer selector for the entrypoint to invoke.
        calldata - a list of integers to pass as calldata to the invoked function.
        signature - a list of integers to pass as signature to the invoked function.
        """
        tx = create_cheatable_invoke_function(
            contract_address=contract_address,
            selector=selector,
            calldata=calldata,
            caller_address=caller_address,
            max_fee=max_fee,
            version=constants.TRANSACTION_VERSION,
            signature=signature,
            entry_point_type=entry_point_type,
            nonce=nonce,
            chain_id=self.general_config.chain_id.value,
        )

        with self.state.copy_and_apply() as state_copy:
            tx_execution_info = await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )

        # Add messages.
        for message in tx_execution_info.get_sorted_l2_to_l1_messages():
            starknet_message = StarknetMessageToL1(
                from_address=message.from_address,
                to_address=message.to_address,
                payload=message.payload,
            )
            self.l2_to_l1_messages_log.append(starknet_message)
            message_hash = starknet_message.get_hash()
            self._l2_to_l1_messages[message_hash] = (
                self._l2_to_l1_messages.get(message_hash, 0) + 1
            )

        # Add events.
        self.events += tx_execution_info.get_sorted_events()

        return tx_execution_info

    @classmethod
    async def empty(
        cls, general_config: Optional[CheatableStarknetGeneralConfig] = None
    ) -> "CheatableStarknetState":
        """
        An updated StarknetState instance introducing additional cheats state/
        """
        if general_config is None:
            general_config = CheatableStarknetGeneralConfig()

        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)

        state = cast(
            CheatableCarriedState,
            await CheatableCarriedState.empty_for_testing(
                shared_state=None, ffc=ffc, general_config=general_config
            ),
        )
        return cls(state=state, general_config=general_config)

    def copy(self) -> "CheatableStarknetState":
        return cast(CheatableStarknetState, super().copy())
