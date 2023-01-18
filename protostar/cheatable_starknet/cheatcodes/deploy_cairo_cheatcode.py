import asyncio
from typing import Any, Callable

from protostar.starknet import CheatcodeException
from protostar.cheatable_starknet.cheaters.contracts import ContractsCheaterException
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode

from protostar.contract_types import PreparedContract


class DeployCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "deploy"

    def build(self) -> Callable[[Any], Any]:
        return self.deploy_prepared

    def deploy_prepared(
        self,
        prepared: PreparedContract,
    ):
        return asyncio.run(self._run_deploy_prepared(prepared))

    async def _run_deploy_prepared(self, prepared: PreparedContract):
        try:
            return await self.cheaters.contracts.deploy_prepared(prepared)
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
