import copy
from starkware.starknet.testing.starknet import Starknet

from typing import Optional

from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.state import StarknetState

class ForkableStarknet(Starknet):
    @classmethod
    async def empty(cls, general_config: Optional[StarknetGeneralConfig] = None) -> "Starknet":
        return ForkableStarknet(state=await StarknetState.empty(general_config=general_config))

    def plug_from_different_state(self, deployed_contact: StarknetContract):
        return StarknetContract(
            state=self.state,
            abi=copy.deepcopy(deployed_contact.abi),
            contract_address=deployed_contact.contract_address,
            deploy_execution_info=copy.deepcopy(deployed_contact.deploy_execution_info),
        )

    def fork(self):
        return ForkableStarknet(state=self.state.copy())
