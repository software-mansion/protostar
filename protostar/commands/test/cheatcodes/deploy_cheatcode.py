import asyncio
from typing import Any, Callable, List

from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.objects import CallInfo
from starkware.starknet.business_logic.transaction.objects import InternalDeploy
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_deploy_transaction_hash,
)

from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract
from protostar.migrator.cheatcodes.migrator_deploy_contract_cheatcode import (
    DeployedContract,
)
from protostar.starknet.cheatcode import Cheatcode


class DeployCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        cheatable_syscall_internal_calls: List[CallInfo],
    ):
        super().__init__(syscall_dependencies)
        # fixes https://github.com/software-mansion/protostar/issues/398
        self.internal_calls = cheatable_syscall_internal_calls

    @property
    def name(self) -> str:
        return "deploy"

    def build(self) -> Callable[[Any], Any]:
        return self.deploy_prepared

    def deploy_prepared(
        self,
        prepared: PreparedContract,
    ):
        deploy_tx_hash = calculate_deploy_transaction_hash(
            version=0,
            contract_address=prepared.contract_address,
            constructor_calldata=prepared.constructor_calldata,
            chain_id=self.general_config.chain_id.value,
        )

        tx = InternalDeploy(
            contract_address=prepared.contract_address,
            contract_address_salt=prepared.salt,
            contract_hash=to_bytes(prepared.class_hash),
            constructor_calldata=prepared.constructor_calldata,
            hash_value=deploy_tx_hash,
            version=0,
        )  # type: ignore

        asyncio.run(self._apply_deploy_tx_updates(tx))

        return DeployedContract(contract_address=prepared.contract_address)

    async def _apply_deploy_tx_updates(self, tx: InternalDeploy):
        with self.cheatable_state.copy_and_apply() as state_copy:
            await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )
