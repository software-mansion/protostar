from collections import defaultdict
import copy
from typing import Dict, List, Optional, cast

from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.state import CastableToAddressSalt, StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext
from protostar.commands.test.starkware.cheatable_execute_entry_point import (
    CheatableInternalInvokeFunction,
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

CastableToAddress = Union[str, int]
CastableToAddressSalt = Union[str, int]

from protostar.commands.test.starkware.types import AddressType, SelectorType


def create_invoke_function(
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

    return CheatableInternalInvokeFunction.create(
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
    )


class CheatableCarriedState(CarriedState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pranked_contracts_map: Dict[int, int] = {}
        self.mocked_calls_map: Dict[
            AddressType, Dict[SelectorType, List[int]]
        ] = defaultdict(dict)
        self.event_selector_to_name_map: Dict[int, str] = {}

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
        self, state: CheatableCarriedState, general_config: StarknetGeneralConfig
    ):
        self.cheatable_carried_state = state
        super().__init__(state, general_config)

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
        print("invoked")
        tx = create_invoke_function(
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
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "CheatableStarknetState":
        """
        An updated StarknetState instance introducing additional cheats state/
        """
        if general_config is None:
            general_config = StarknetGeneralConfig()

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


class ForkableStarknet(Starknet):
    """
    Modified version of Starknet from testing framework.
    It introduces additional cheats state, and can be cheaply forked.
    """

    def __init__(self, state: CheatableStarknetState):
        self.cheatable_state = state
        super().__init__(state)

    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "ForkableStarknet":
        return ForkableStarknet(
            state=await CheatableStarknetState.empty(general_config=general_config)
        )

    def copy_and_adapt_contract(self, deployed_contract: StarknetContract):
        return StarknetContract(
            state=self.state,
            abi=copy.deepcopy(deployed_contract.abi),
            contract_address=deployed_contract.contract_address,
            deploy_execution_info=copy.deepcopy(
                deployed_contract.deploy_execution_info
            ),
        )

    def fork(self):
        return ForkableStarknet(state=self.cheatable_state.copy())

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        source: Optional[str] = None,
        contract_class: Optional[ContractClass] = None,
        contract_address_salt: Optional[CastableToAddressSalt] = None,
        cairo_path: Optional[List[str]] = None,
        constructor_calldata: Optional[List[int]] = None,
    ) -> StarknetContract:
        starknet_contract = await super().deploy(
            source=source,
            contract_class=contract_class,
            contract_address_salt=contract_address_salt,
            cairo_path=cairo_path,
            constructor_calldata=constructor_calldata,
        )

        self.cheatable_state.cheatable_carried_state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            starknet_contract.event_manager._selector_to_name
        )

        return starknet_contract
