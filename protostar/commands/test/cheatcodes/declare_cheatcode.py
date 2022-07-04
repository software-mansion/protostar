import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List

from starkware.python.utils import from_bytes
from starkware.starknet.business_logic.internal_transaction import InternalDeclare
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import EventManager, get_abi

from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.starkware.contract_utils import get_contract_class


@dataclass
class DeclaredContract:
    class_hash: int


class DeclareCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        disable_hint_validation: bool,
        cairo_path: List[str],
    ):
        super().__init__(syscall_dependencies)
        self._disable_hint_validation_in_external_contracts = disable_hint_validation
        self._cairo_path = cairo_path

    @property
    def name(self) -> str:
        return "declare"

    def build(self) -> Callable[[Any], Any]:
        return self.declare

    def declare(self, contract_path_str: str) -> DeclaredContract:
        declared_class = asyncio.run(self._declare_contract(Path(contract_path_str)))
        class_hash = declared_class.class_hash

        self.state.class_hash_to_contract_abi_map[class_hash] = declared_class.abi

        return DeclaredContract(class_hash)

    async def _declare_contract(self, contract_path: Path):
        contract_class = get_contract_class(
            source=str(contract_path),
            cairo_path=self._cairo_path,
            disable_hint_validation=self._disable_hint_validation_in_external_contracts,
        )

        tx = await InternalDeclare.create_for_testing(
            ffc=self.state.ffc,
            contract_class=contract_class,
            chain_id=self.general_config.chain_id.value,
        )

        with self.state.copy_and_apply() as state_copy:
            tx_execution_info = await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )

        abi = get_abi(contract_class=contract_class)
        event_manager = EventManager(abi=abi)
        self.state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            event_manager._selector_to_name
        )
        # pylint: disable=protected-access
        for event_name in event_manager._selector_to_name.values():
            self.state.event_name_to_contract_abi_map[event_name] = abi

        class_hash = tx_execution_info.call_info.class_hash
        assert class_hash is not None
        return DeclaredClass(
            class_hash=from_bytes(class_hash),
            abi=get_abi(contract_class=contract_class),
        )
