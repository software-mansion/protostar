from protostar.architecture import UseCase

from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput
from .multicall_protocols import MulticallGatewayProtocol, MulticallSignerProtocol
from .call_resolver import CallResolver


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    def __init__(
        self,
        gateway: MulticallGatewayProtocol,
        signer: MulticallSignerProtocol,
        call_resolver: CallResolver,
    ) -> None:
        super().__init__()
        self._signer = signer
        self._gateway = gateway
        self._call_resolver = call_resolver

    async def execute(self, data: MulticallInput):
        resolved_calls = await self._call_resolver.resolve(data.calls)
        signed_transaction = await self._signer.sign_multicall_transaction(
            resolved_calls
        )
        return await self._gateway.send_multicall_transaction(signed_transaction)
