from typing import List, Optional, Tuple, Union, cast

from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.state import CarriedState
from starkware.starknet.business_logic.transaction_execution_objects import (
    TransactionExecutionInfo,
)
from starkware.starknet.definitions import fields
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.gateway.transaction import Deploy
from starkware.starknet.testing.state import StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext

from src.commands.test.cheatcodes.internal_transaction import CheatableInternalDeploy

CastableToAddress = Union[str, int]
CastableToAddressSalt = Union[str, int]


class CheatableStarknetState(StarknetState):
    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "StarknetState":
        """
        Creates a new StarknetState instance.
        """
        if general_config is None:
            general_config = StarknetGeneralConfig()

        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)
        state = await CarriedState.create_empty_for_test(
            shared_state=None, ffc=ffc, general_config=general_config
        )

        return cls(state=state, general_config=general_config)

    async def deploy(
        self,
        contract_definition: ContractDefinition,
        constructor_calldata: List[int],
        contract_address_salt: Optional[CastableToAddressSalt] = None,
    ) -> Tuple[int, TransactionExecutionInfo]:
        """
        Deploys a contract. Returns the contract address and the execution info.

        Args:
        contract_definition - a compiled StarkNet contract returned by compile_starknet_files().
        contract_address_salt - If supplied, a hexadecimal string or an integer representing
        the salt to use for deploying. Otherwise, the salt is randomized.
        """

        if contract_address_salt is None:
            contract_address_salt = fields.ContractAddressSalt.get_random_value()
        if isinstance(contract_address_salt, str):
            contract_address_salt = int(contract_address_salt, 16)
        assert isinstance(contract_address_salt, int)

        external_tx = Deploy(
            contract_address_salt=contract_address_salt,
            contract_definition=contract_definition,
            constructor_calldata=constructor_calldata,
        )
        tx = cast(
            CheatableInternalDeploy,
            CheatableInternalDeploy.from_external(
                external_tx=external_tx, general_config=self.general_config
            ),
        )

        with self.state.copy_and_apply() as state_copy:
            tx_execution_info = await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )

        return tx.contract_address, tx_execution_info
