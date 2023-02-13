from typing import Callable

from protostar.cheatable_starknet.controllers.contracts import ContractsController
from protostar.starknet import Address, Selector

from .callable_hint_local import CallableHintLocal


class MockCallHintLocal(CallableHintLocal):
    def __init__(self, controller: ContractsController) -> None:
        super().__init__()
        self._controller = controller

    @property
    def name(self) -> str:
        return "mock_call"

    def _build(self) -> Callable:
        return self.mock_call

    def mock_call(
        self, target_address: int, entrypoint: str, response: list[int]
    ) -> None:
        return self._controller.mock_call(
            target_address=Address.from_user_input(target_address),
            entrypoint=Selector(entrypoint),
            response=response,
        )
