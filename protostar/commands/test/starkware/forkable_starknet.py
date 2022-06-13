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

from protostar.commands.test.starkware.types import AddressType, SelectorType


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
