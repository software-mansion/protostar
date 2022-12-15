from dataclasses import dataclass

from protostar.starknet import Calldata


@dataclass
class InvokeInput:
    calldata: Calldata


@dataclass
class UnsignedInvokeTransaction:
    pass


@dataclass
class SignedInvokeTransaction:
    pass


@dataclass
class ClientResponse:
    pass


@dataclass
class InvokeOutput:
    pass
