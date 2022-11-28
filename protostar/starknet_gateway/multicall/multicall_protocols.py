from abc import abstractmethod
from dataclasses import dataclass

from typing_extensions import Protocol

from protostar.starknet.address import Address

from .multicall_output import MulticallOutput


@dataclass
class MulticallUnsignedTransaction:
    calldata: list[int]


@dataclass
class MulticallSignedTransaction(MulticallUnsignedTransaction):
    pass


@dataclass
class ResolvedCall:
    address: Address
    selector: int
    calldata: list[int]


@dataclass
class MulticallSignerProtocol(Protocol):
    @abstractmethod
    async def sign_multicall_transaction(
        self, unsigned_transaction: MulticallUnsignedTransaction
    ) -> MulticallSignedTransaction:
        ...


class MulticallGatewayProtocol(Protocol):
    @abstractmethod
    async def send_multicall_transaction(
        self, transaction: MulticallSignedTransaction
    ) -> MulticallOutput:
        ...
