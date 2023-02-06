import asyncio
from typing import Any, Callable, Optional

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers.contracts import (
    ContractsCheaterException,
    ContractsController,
    DeclaredContract,
    PreparedContract,
)
from protostar.starknet import CheatcodeException
from protostar.starknet.data_transformer import CairoOrPythonData


class PrepareHintLocal(CallableHintLocal):
    salt_nonce = 1

    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "prepare"

    def _build(self) -> Callable[[Any], Any]:
        return self.prepare

    def prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: Optional[CairoOrPythonData] = None,
        salt: Optional[int] = None,
    ) -> PreparedContract:
        return asyncio.run(
            self._prepare(
                declared=declared, constructor_calldata=constructor_calldata, salt=salt
            )
        )

    async def _prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: Optional[CairoOrPythonData] = None,
        salt: Optional[int] = None,
    ) -> PreparedContract:
        contract_salt = PrepareHintLocal.salt_nonce
        PrepareHintLocal.salt_nonce += 1
        salt = salt or contract_salt
        constructor_calldata = constructor_calldata or []

        try:
            return await self._contracts_controller.prepare(
                declared=declared, constructor_calldata=constructor_calldata, salt=salt
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
