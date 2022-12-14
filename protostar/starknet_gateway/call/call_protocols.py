from abc import abstractmethod
from typing import Protocol

from protostar.starknet import Address, AbiType

from .call_structs import (
    CallClientPayload,
    CallClientResponse,
    PythonCalldata,
    CairoCalldata,
)


class CallClientProtocol(Protocol):
    @abstractmethod
    async def call(self, payload: CallClientPayload) -> CallClientResponse:
        ...


class ContractAddressToAbiConverterProtocol(Protocol):
    async def convert(self, contract_address: Address) -> AbiType:
        ...


class DataTransformerProtocol(Protocol):
    @abstractmethod
    async def convert_to_cairo_calldata(
        self, abi: AbiType, python_calldata: PythonCalldata
    ) -> CairoCalldata:
        ...
