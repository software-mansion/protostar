import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from starkware.starknet.business_logic.transaction.objects import InternalDeclare
from starkware.starknet.public.abi import AbiType
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import EventManager

from protostar.compiler import ProjectCompiler
from protostar.starknet import Cheatcode, KeywordOnlyArgumentCheatcodeException


@dataclass
class DeclaredContract:
    class_hash: int


class DeclareCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract: str,
        *args: Any,
    ) -> DeclaredContract:
        ...


class DeclareCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        project_compiler: ProjectCompiler,
    ):
        super().__init__(syscall_dependencies)
        self._project_compiler = project_compiler

    @property
    def name(self) -> str:
        return "declare"

    def build(self) -> DeclareCheatcodeProtocol:
        return self.declare

    def declare(
        self,
        contract: str,
        *args: Any,
    ) -> DeclaredContract:
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        declared_class = asyncio.run(self._declare_contract(contract))
        assert declared_class
        class_hash = declared_class.class_hash

        self.cheatable_state.class_hash_to_contract_abi_map[
            class_hash
        ] = declared_class.abi

        self.cheatable_state.class_hash_to_contract_path_map[class_hash] = Path(
            contract
        )

        return DeclaredContract(class_hash)

    async def _declare_contract(self, contract: str):
        contract_class = (
            self._project_compiler.compile_contract_from_contract_identifier(contract)
        )

        tx = InternalDeclare.create_deprecated(
            contract_class=contract_class,
            chain_id=self.general_config.chain_id.value,
            sender_address=DEFAULT_DECLARE_SENDER_ADDRESS,
            max_fee=0,
            version=0,
            signature=[],
            nonce=0,
        )

        with self.cheatable_state.copy_and_apply() as state_copy:
            await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )

        self._add_event_abi_to_state(contract_class.abi)
        class_hash = tx.class_hash
        assert class_hash is not None
        await self.cheatable_state.set_contract_class(class_hash, contract_class)

        return DeclaredClass(
            class_hash=class_hash,
            abi=contract_class.abi,
        )

    def _add_event_abi_to_state(self, abi: AbiType):
        event_manager = EventManager(abi=abi)
        self.cheatable_state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            event_manager._selector_to_name
        )
        # pylint: disable=protected-access
        for event_name in event_manager._selector_to_name.values():
            self.cheatable_state.event_name_to_contract_abi_map[event_name] = abi
