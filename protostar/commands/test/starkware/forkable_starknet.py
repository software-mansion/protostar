import copy
from typing import List, Optional

from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.state import CastableToAddressSalt
from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.commands.test.starkware.cheatable_state import CheatableStarknetState


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
        cls, general_config: Optional[CheatableStarknetGeneralConfig] = None
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
