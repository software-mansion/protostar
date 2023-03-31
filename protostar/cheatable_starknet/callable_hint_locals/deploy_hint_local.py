import asyncio
from typing import Any, Callable

from protostar.starknet import CheatcodeException
from protostar.cheatable_starknet.controllers.contracts import (
    ContractsCheaterException,
    ContractsController,
    PreparedContract,
)

from .callable_hint_local import CallableHintLocal


class DeployHintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "deploy_tp"

    def _build(self) -> Callable[[list[int], int, int], Any]:
        return self.deploy_prepared_tp

    def deploy_prepared_tp(
        self,
        constructor_calldata: list[int],
        contract_address: int,
        class_hash: int,
    ):
        return self.deploy_prepared(
            PreparedContract(
                constructor_calldata=constructor_calldata,
                contract_address=contract_address,
                class_hash=class_hash,
                salt=0,
            )
        )

    def deploy_prepared(
        self,
        prepared: PreparedContract,
    ):
        return asyncio.run(self._run_deploy_prepared(prepared))

    async def _run_deploy_prepared(self, prepared: PreparedContract):
        try:
            return await self._contracts_controller.deploy_prepared(prepared)
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
