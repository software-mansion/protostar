from abc import abstractmethod
from typing import Protocol

from protostar.starknet import Address, AbiType

from .call_structs import CallClientPayload, CallClientResponse


class ClientProtocol(Protocol):
    @abstractmethod
    async def call(self, payload: CallClientPayload) -> CallClientResponse:
        ...


class AbiResolverProtocol(Protocol):
    async def resolve(self, address: Address) -> AbiType:
        ...
