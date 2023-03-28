import asyncio
from typing import Any, Callable

from protostar.starknet import CheatcodeException
from protostar.cheatable_starknet.controllers.contracts import (
    ContractsCheaterException,
    ContractsController,
    PreparedContract,
)

from .callable_hint_local import CallableHintLocal


class DeployCairo0HintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "deploy_tp_cairo0"

    def _build(self) -> Callable[[Any], Any]:
        return self.deploy_cairo0_prepared

    def deploy_cairo0_prepared(
        self,
        prepared: PreparedContract,
    ):
        return asyncio.run(self._run_deploy_cairo0_prepared(prepared))

    async def _run_deploy_cairo0_prepared(self, prepared: PreparedContract):
        try:
            return await self._contracts_controller.deploy_cairo0_prepared(prepared)
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
