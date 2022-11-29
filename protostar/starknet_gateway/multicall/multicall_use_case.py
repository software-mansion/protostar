from protostar.architecture import UseCase
from protostar.starknet.selector import Selector

from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput
from .multicall_protocols import (
    MulticallClientProtocol,
    InvokeUnsignedTransaction,
    AccountManagerProtocol,
)
from .call_resolver import CallResolver
from .resolved_calls_to_calldata_converter import ResolvedCallsToCalldataConverter


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    def __init__(
        self,
        client: MulticallClientProtocol,
        account_manager: AccountManagerProtocol,
        call_resolver: CallResolver,
        resolved_calls_to_calldata_converter: ResolvedCallsToCalldataConverter,
    ) -> None:
        super().__init__()
        self._account_manager = account_manager
        self._client = client
        self._call_resolver = call_resolver
        self._resolved_calls_to_calldata_converter = (
            resolved_calls_to_calldata_converter
        )

    async def execute(self, data: MulticallInput):
        resolved_calls = await self._call_resolver.resolve(data.calls)
        calldata = self._resolved_calls_to_calldata_converter.convert(resolved_calls)
        unsigned_tx = InvokeUnsignedTransaction(
            contract_address=self._account_manager.get_account_address(),
            calldata=calldata,
            selector=Selector("__execute__"),
        )
        signed_transaction = await self._account_manager.sign_invoke_transaction(
            unsigned_tx
        )
        return await self._client.send_multicall_transaction(signed_transaction)
