from protostar.architecture import UseCase, Mapper

from .multicall_input import MulticallInput, CallBase
from .multicall_output import MulticallOutput
from .multicall_protocols import (
    MulticallGatewayProtocol,
    MulticallSignerProtocol,
    ResolvedCall,
)


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    def __init__(
        self,
        gateway: MulticallGatewayProtocol,
        signer: MulticallSignerProtocol,
        call_mapper: Mapper[CallBase, ResolvedCall],
    ) -> None:
        super().__init__()
        self._signer = signer
        self._gateway = gateway
        self._call_mapper = call_mapper

    async def execute(self, data: MulticallInput):
        resolved_calls = [await self._call_mapper.map(call) for call in data.calls]
        signed_transaction = await self._signer.sign_multicall_transaction(
            resolved_calls
        )
        return await self._gateway.send_multicall_transaction(signed_transaction)
