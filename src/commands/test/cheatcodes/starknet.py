from typing import Optional

from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.starknet import Starknet

from src.commands.test.cheatcodes.state import CheatableStarknetState


class CheatableStarknet:
    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> Starknet:
        return Starknet(
            state=await CheatableStarknetState.empty(general_config=general_config)
        )
