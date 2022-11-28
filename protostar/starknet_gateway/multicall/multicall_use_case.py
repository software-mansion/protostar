from protostar.architecture import UseCase

from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput
from .multicall_protocols import (
    MulticallGatewayProtocol,
    MulticallSignerProtocol,
    MulticallUnsignedTransaction,
)
from .call_resolver import CallResolver
from .resolved_calls_to_calldata_converter import ResolvedCallsToCalldataConverter


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    def __init__(
        self,
        gateway: MulticallGatewayProtocol,
        signer: MulticallSignerProtocol,
        call_resolver: CallResolver,
        resolved_calls_to_calldata_converter: ResolvedCallsToCalldataConverter,
    ) -> None:
        super().__init__()
        self._signer = signer
        self._gateway = gateway
        self._call_resolver = call_resolver
        self._resolved_calls_to_calldata_converter = (
            resolved_calls_to_calldata_converter
        )

    async def execute(self, data: MulticallInput):
        resolved_calls = await self._call_resolver.resolve(data.calls)
        calldata = self._resolved_calls_to_calldata_converter.convert(resolved_calls)
        unsigned_tx = MulticallUnsignedTransaction(calldata=calldata)
        signed_transaction = await self._signer.sign_multicall_transaction(unsigned_tx)
        return await self._gateway.send_multicall_transaction(signed_transaction)
