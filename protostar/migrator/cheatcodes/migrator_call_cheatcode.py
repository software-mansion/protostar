import asyncio
from typing import Callable, Dict, Any, Optional

from starknet_py.net.models import AddressRepresentation

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import GatewayFacade


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

    def build(self) -> Callable:
        return self.call

    def call(
        self,
        address: AddressRepresentation,
        function_name: str,
        inputs: Optional[Dict[str, Any]] = None,
    ):

        output = asyncio.run(
            self._gateway_facade.call(
                address=address,
                function_name=function_name,
                inputs=inputs,
            )
        )
