import asyncio
from typing import Callable, Dict, Any, Optional

from starknet_py.net.models import AddressRepresentation

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import GatewayFacade


class MigratorInvokeCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade

    @property
    def name(self) -> str:
        return "invoke"

    def build(self) -> Callable:
        return self.invoke

    # TODO: consider CheatcodeNetworkConfig instead of wait_for_acceptance
    async def invoke(
        self,
        address: AddressRepresentation,
        function_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        wait_for_acceptance: bool = False,
    ):

        asyncio.run(
            self._gateway_facade.invoke(
                address=address,
                function_name=function_name,
                inputs=inputs,
                wait_for_acceptance=wait_for_acceptance,
            )
        )
