from typing import Union

from starknet_py.net.udc_deployer.deployer import Deployer

from protostar.protostar_exception import ProtostarException
from protostar.starknet import Address
from protostar.starknet.selector import Selector

from .multicall_structs import (
    Call,
    InvokeCall,
    DeployCall,
    Identifier,
    MulticallInputCalldata,
    ResolvedCall,
)


class CallResolver:
    def __init__(self) -> None:
        self._deploy_call_name_to_address: dict[Identifier, Address] = {}
        self._deployer = Deployer()

    async def resolve(self, calls: list[Call]) -> list[ResolvedCall]:
        return [self._resolve_single_call(call) for call in calls]

    def get_deploy_call_name_to_address(self) -> dict[Identifier, Address]:
        return self._deploy_call_name_to_address

    def _resolve_single_call(self, call: Call) -> ResolvedCall:
        if isinstance(call, DeployCall):
            return self._resolve_deploy_call(call)
        return self._resolve_invoke_call(call)

    def _resolve_deploy_call(self, deploy_call: DeployCall) -> ResolvedCall:
        deployment_call = self._deployer.create_deployment_call_raw(
            class_hash=deploy_call.class_hash
        )
        if deploy_call.address_alias:
            self._deploy_call_name_to_address[deploy_call.address_alias] = Address(
                deployment_call.address
            )
        return ResolvedCall(
            address=Address(deployment_call.udc.to_addr),
            calldata=deployment_call.udc.calldata,
            selector=Selector(deployment_call.udc.selector),
        )

    def _resolve_invoke_call(self, invoke_call: InvokeCall) -> ResolvedCall:
        return ResolvedCall(
            address=self._resolve_address(invoke_call.address),
            calldata=self._resolve_calldata(invoke_call.calldata),
            selector=invoke_call.selector,
        )

    def _resolve_address(self, name_or_address: Union[Identifier, Address]) -> Address:
        if isinstance(name_or_address, Address):
            return name_or_address
        name = name_or_address
        if name not in self._deploy_call_name_to_address:
            raise UnknownNameException(message=f"Couldn't resolve name: {name}")
        return self._deploy_call_name_to_address[name]

    def _resolve_calldata(self, calldata: MulticallInputCalldata) -> list[int]:
        result: list[int] = []
        for value in calldata:
            if isinstance(value, int):
                result.append(value)
                continue
            if value not in self._deploy_call_name_to_address:
                raise UnknownNameException(message=f"Couldn't resolve name: {value}")
            result.append(int(self._deploy_call_name_to_address[value]))
        return result


class UnknownNameException(ProtostarException):
    def __init__(self, message: str):
        super().__init__(message)
