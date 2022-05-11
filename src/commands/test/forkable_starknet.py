from collections import defaultdict
import copy
from typing import Optional

from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.business_logic.state.state import CarriedState
from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.testing.state import StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext

import copy

from starkware.cairo.lang.vm.crypto import pedersen_hash_func

from starkware.starknet.business_logic.state.state import CarriedState, SharedState
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext

import copy
from collections import defaultdict
from typing import Dict, Optional,  Tuple



from starkware.starknet.business_logic.state.objects import ContractCarriedState, ContractState
from starkware.starknet.definitions.general_config import  StarknetGeneralConfig
from starkware.storage.storage import FactFetchingContext


class ForkableStarknet(Starknet):
    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "Starknet":
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

    @classmethod
    async def empty(cls, general_config: Optional[StarknetGeneralConfig] = None) -> "StarknetState":
        """
        Creates a new StarknetState instance.
        """
        if general_config is None:
            general_config = StarknetGeneralConfig()

        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)
        
        state = await CheatableCarriedState.empty_for_testing(
            shared_state=None, ffc=ffc, general_config=general_config
        )
        return cls(state=state, general_config=general_config)



class CheatableCarriedState(CarriedState):
    placeholder: int = 1
