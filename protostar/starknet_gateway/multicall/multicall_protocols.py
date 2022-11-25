from abc import abstractmethod
from dataclasses import dataclass

from typing_extensions import Protocol

from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput


@dataclass
class MulticallSignedTransaction:
    pass


@dataclass
class MulticallSignerProtocol(Protocol):
    @abstractmethod
    async def sign_multicall_transaction(
        self, transaction: MulticallInput
    ) -> MulticallSignedTransaction:
        ...


class GatewayProtocol(Protocol):
    @abstractmethod
    async def send_multicall_transaction(
        self, transaction: MulticallSignedTransaction
    ) -> MulticallOutput:
        ...
