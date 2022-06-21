import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional, cast

from starkware.python.utils import from_bytes, to_bytes
from starkware.starknet.business_logic.internal_transaction import InternalDeclare
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)
from starkware.starknet.core.os.syscall_utils import initialize_contract_state
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import (
    EventManager,
    get_abi,
    get_contract_class,
)

from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)

if TYPE_CHECKING:
    from protostar.commands.test.starkware.cheatable_state import CheatableCarriedState


@dataclass
class DeclaredContract:
    class_hash: int


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class DeployContractCheatcode(CheatableSysCallHandler):
    salt_nonce = 1

    @property
    def cheatable_general_config(self) -> CheatableStarknetGeneralConfig:
        return cast(CheatableStarknetGeneralConfig, self.general_config)

    def deploy_prepared(self, prepared: PreparedContract):
        class_hash_bytes = to_bytes(prepared.class_hash)
        future = asyncio.run_coroutine_threadsafe(
            coro=initialize_contract_state(
                state=self.state,
                class_hash=class_hash_bytes,
                contract_address=prepared.contract_address,
            ),
            loop=self.loop,
        )
        future.result()

        self.execute_constructor_entry_point(
            contract_address=prepared.contract_address,
            class_hash_bytes=class_hash_bytes,
            constructor_calldata=prepared.constructor_calldata,
        )
        return DeployedContract(prepared.contract_address)

    def prepare_declared(
        self, declared: DeclaredContract, constructor_calldata=None
    ) -> PreparedContract:
        constructor_calldata = constructor_calldata or []
        contract_address: int = calculate_contract_address_from_hash(
            salt=DeployContractCheatcode.salt_nonce,
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=self.contract_address,
        )
        self.cheatable_state.contract_address_to_class_hash_map[
            contract_address
        ] = declared.class_hash
        DeployContractCheatcode.salt_nonce += 1
        return PreparedContract(
            constructor_calldata, contract_address, declared.class_hash
        )

    def declare(self, contract_path_str: str) -> DeclaredContract:
        class_hash = asyncio.run(self._declare_contract(contract_path_str)).class_hash

        self.cheatable_state.class_hash_to_contract_path_map[class_hash] = Path(
            contract_path_str
        )
        return DeclaredContract(class_hash)

    async def _declare_contract(self, contract_path_str: str):
        contract_class = get_contract_class(
            source=contract_path_str,
            cairo_path=self.cheatable_general_config.cheatcodes_cairo_path,
        )

        tx = await InternalDeclare.create_for_testing(
            ffc=self.state.ffc,
            contract_class=contract_class,
            chain_id=self.general_config.chain_id.value,
        )

        abi = get_abi(contract_class=contract_class)
        event_manager = EventManager(abi=abi)
        self.cheatable_state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            event_manager._selector_to_name
        )
        with self.cheatable_state.copy_and_apply() as state_copy:
            tx_execution_info = await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )

        class_hash = tx_execution_info.call_info.class_hash
        assert class_hash is not None
        return DeclaredClass(
            class_hash=from_bytes(class_hash),
            abi=abi,
        )


def build_deploy_contract(
    manager,
) -> Callable[[Path, List[int]], DeployedContract]:  # TODO add transformer
    """
    Syntactic sugar for contract deployment compatible with the old interface
    """

    def deploy_contract(
        path: Path, constructor_calldata: Optional[List[int]] = None
    ) -> DeployedContract:
        declared = manager.declare(path)
        prepared = manager.prepare_declared(declared, constructor_calldata)
        return manager.deploy_prepared(prepared)

    return deploy_contract
