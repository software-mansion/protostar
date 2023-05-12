import copy
from typing import List, Optional, cast

from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.contract import StarknetContract
from starkware.starknet.testing.contract_utils import CastableToFelt, CastableToAddress
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.state import CastableToAddressSalt

from protostar.starknet.cheatable_state import CheatableStarknetState


class ForkableStarknet(Starknet):
    """
    Modified version of Starknet from testing framework.
    It introduces additional cheats state, and can be cheaply forked.
    """

    def __init__(self, state: CheatableStarknetState):
        super().__init__(state)

    @property
    def cheatable_state(self) -> CheatableStarknetState:
        return cast(CheatableStarknetState, self.state)

    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "ForkableStarknet":
        return ForkableStarknet(
            state=await CheatableStarknetState.empty(general_config=general_config)
        )

    def copy_and_adapt_contract(self, deployed_contract: StarknetContract):
        return StarknetContract(
            state=self.cheatable_state,
            abi=copy.deepcopy(deployed_contract.abi),
            contract_address=deployed_contract.contract_address,
            constructor_call_info=copy.deepcopy(
                deployed_contract.constructor_call_info
            ),
        )

    def fork(self):
        return ForkableStarknet(state=self.cheatable_state.copy())

    async def deploy(
        self,
        class_hash: CastableToFelt,
        contract_address_salt: Optional[CastableToAddressSalt] = None,
        constructor_calldata: Optional[List[int]] = None,
        sender_address: Optional[CastableToAddress] = None,
    ) -> StarknetContract:
        starknet_contract = await super().deploy(
            class_hash=class_hash,
            contract_address_salt=contract_address_salt,
            constructor_calldata=constructor_calldata,
        )

        self.cheatable_state.cheatable_state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            starknet_contract.event_manager._selector_to_name
        )
        # pylint: disable=protected-access
        for event_name in starknet_contract.event_manager._selector_to_name.values():
            self.cheatable_state.cheatable_state.event_name_to_contract_abi_map[
                event_name
            ] = starknet_contract.abi

        return starknet_contract
