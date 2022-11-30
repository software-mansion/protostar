from typing import Union

from starknet_py.net.udc_deployer.deployer import Deployer

from protostar.protostar_exception import ProtostarException
from protostar.starknet import Address
from protostar.starknet.selector import Selector

from .multicall_structs import (
    CallBase,
    InvokeCall,
    DeployCall,
    DeployCallName,
    ResolvedCall,
)


class CallResolver:
    def __init__(self) -> None:
        self._deploy_call_name_to_address: dict[DeployCallName, Address] = {}
        self._deployer = Deployer()

    async def resolve(self, calls: list[CallBase]) -> list[ResolvedCall]:
        return [self._resolve_single_call(call) for call in calls]

    def get_deploy_call_name_to_address(self) -> dict[DeployCallName, Address]:
        return self._deploy_call_name_to_address

    def _resolve_single_call(self, call: CallBase) -> ResolvedCall:
        if isinstance(call, DeployCall):
            return self._resolve_deploy_call(call)
        if isinstance(call, InvokeCall):
            return self._resolve_invoke_call(call)
        assert False, f"Unknown call: {call}"

    def _resolve_deploy_call(self, deploy_call: DeployCall) -> ResolvedCall:
        deployment_call = self._deployer.create_deployment_call_raw(
            class_hash=deploy_call.class_hash
        )
        if deploy_call.name:
            self._deploy_call_name_to_address[deploy_call.name] = Address(
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
            calldata=invoke_call.calldata,
            selector=invoke_call.selector,
        )

    def _resolve_address(
        self, name_or_address: Union[DeployCallName, Address]
    ) -> Address:
        if isinstance(name_or_address, Address):
            return name_or_address
        name = name_or_address
        if name not in self._deploy_call_name_to_address:
            raise UnknownNameException(message=f"Couldn't resolve name: {name}")
        return self._deploy_call_name_to_address[name]


class UnknownNameException(ProtostarException):
    def __init__(self, message: str):
        super().__init__(message)
