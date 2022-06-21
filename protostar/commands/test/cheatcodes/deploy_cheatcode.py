import asyncio
from dataclasses import dataclass
from starkware.python.utils import to_bytes
from starkware.starknet.core.os.syscall_utils import (
    initialize_contract_state,
)

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class DeployCheatcode(Cheatcode):
    @staticmethod
    def name() -> str:
        return "deploy"

    @staticmethod
    def implementation() -> str:
        return "deploy"

    def deploy(self, prepared: PreparedContract):
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
