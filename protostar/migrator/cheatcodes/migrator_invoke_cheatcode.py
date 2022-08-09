import asyncio
from typing import Dict, Any, Optional
from typing_extensions import Protocol

from starknet_py.net.models import AddressRepresentation

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import GatewayFacade
from protostar.commands.test.test_environment_exceptions import (
    KeywordOnlyArgumentCheatcodeException,
)

from .network_config import CheatcodeNetworkConfig, ValidatedCheatcodeNetworkConfig


class InvokeCheatcodeProtocol(Protocol):
    # pylint: disable=keyword-arg-before-vararg
    def __call__(
        self,
        address: AddressRepresentation,
        function_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        *args,
        config: Optional[Any] = None,
    ) -> Any:
        ...


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

    def build(self) -> InvokeCheatcodeProtocol:
        return self.invoke

    # pylint: disable=keyword-arg-before-vararg
    async def invoke(
        self,
        address: AddressRepresentation,
        function_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        *args,
        config: Optional[CheatcodeNetworkConfig] = None,
    ):
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(
            config or CheatcodeNetworkConfig()
        )
        asyncio.run(
            self._gateway_facade.invoke(
                address=address,
                function_name=function_name,
                inputs=inputs,
                wait_for_acceptance=validated_config.wait_for_acceptance,
            )
        )
