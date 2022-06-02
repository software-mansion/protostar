import copy
from typing import Mapping, Optional

from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.state import StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext


class ForkableStarknet(Starknet):
    """
    Modified version of Starknet from testing framework.
    It introduces additional cheats state, and can be cheaply forked.
    """

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
        return ForkableStarknet(state=self.state.copy())


class CheatableStarknetState(StarknetState):
    """
    Modified version of StarknetState from testing framework.
    It uses extended version of CarriedState - CheatableCarriedState.
    """

    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "StarknetState":
        """
        An updated StarknetState instance introducing additional cheats state/
        """
        if general_config is None:
            general_config = StarknetGeneralConfig()

        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)

        state = await CheatableCarriedState.empty_for_testing(
            shared_state=None, ffc=ffc, general_config=general_config
        )
        return cls(state=state, general_config=general_config)


class CheatableCarriedState(CarriedState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pranked_contracts_map: Mapping[int, int] = {}
