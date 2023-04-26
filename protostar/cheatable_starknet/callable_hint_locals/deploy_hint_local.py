import asyncio
from typing import Any, Callable

from starkware.starkware_utils.error_handling import StarkException

from protostar.cheatable_starknet.controllers.contracts import (
    ContractsController,
    PreparedContract,
    ConstructorInvocationException,
)
from protostar.cheatable_starknet.controllers.transaction_revert_exception import (
    TransactionRevertException,
)

from .callable_hint_local import CallableHintLocal


class DeployHintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "deploy_impl"

    def _build(self) -> Callable[[list[int], int, int], Any]:
        return self.deploy_prepared_impl

    def deploy_prepared_impl(
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
        except ConstructorInvocationException as exc:
            raise TransactionRevertException(exc.message, exc) from exc
        except StarkException as exc:
            raise TransactionRevertException(exc.message or exc.code.name, exc) from exc
