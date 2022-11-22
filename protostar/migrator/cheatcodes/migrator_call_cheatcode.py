import asyncio
from typing import Any, Optional

from typing_extensions import Protocol

from protostar.starknet import Cheatcode, CheatcodeException, Address
from protostar.starknet_gateway import (
    ContractNotFoundException,
    GatewayFacade,
    UnknownFunctionException,
)
from protostar.starknet.data_transformer import CairoOrPythonData


class CallCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[CairoOrPythonData] = None,
    ) -> Any:
        ...


class MigratorCallCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade

    @property
    def name(self) -> str:
        return "call"

    def build(self) -> CallCheatcodeProtocol:
        return self.call

    def call(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[CairoOrPythonData] = None,
    ):
        try:
            return asyncio.run(
                self._gateway_facade.call(
                    address=Address.from_user_input(contract_address),
                    function_name=function_name,
                    inputs=inputs,
                )
            )
        except (UnknownFunctionException, ContractNotFoundException) as err:
            raise CheatcodeException(self, err.message) from err
