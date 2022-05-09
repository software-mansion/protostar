import copy
from typing import Optional

from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.state import StarknetState


class ForkableStarknet(Starknet):
    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "Starknet":
        return ForkableStarknet(
            state=await StarknetState.empty(general_config=general_config)
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
