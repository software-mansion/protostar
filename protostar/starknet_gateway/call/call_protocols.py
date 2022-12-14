from abc import abstractmethod
from typing import Optional, Protocol

from protostar.starknet import Address, AbiType

from .call_structs import CallPayload, CallResponse


class ClientProtocol(Protocol):
    @abstractmethod
    async def send_call(self, payload: CallPayload) -> CallResponse:
        ...


class AbiResolverProtocol(Protocol):
    async def resolve(self, address: Address) -> Optional[AbiType]:
        ...
