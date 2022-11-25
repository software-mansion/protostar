from protostar.architecture import UseCase

from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput
from .multicall_protocols import GatewayProtocol, MulticallSignerProtocol


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    def __init__(
        self, gateway: GatewayProtocol, signer: MulticallSignerProtocol
    ) -> None:
        super().__init__()
        self._signer = signer
        self._gateway = gateway

    async def execute(self, data: MulticallInput):
        signed_transaction = await self._signer.sign_multicall_transaction(data)
        await self._gateway.send_multicall_transaction(signed_transaction)
        return MulticallOutput(transaction_hash=123)
