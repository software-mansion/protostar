from protostar.starknet import CairoDataRepresentation

from .invoke_structs import InvokeInput, InvokeOutput, UnsignedInvokeTransaction
from .invoke_protocols import AccountManagerProtocol, ClientProtocol


class InvokeUseCase:
    def __init__(
        self, client: ClientProtocol, account_manager: AccountManagerProtocol
    ) -> None:
        self._client = client
        self._account_manager = account_manager

    async def execute(self, input_data: InvokeInput) -> InvokeOutput:
        cairo_calldata = self._translate_calldata_if_necessary(input_data)
        unsigned_invoke_transaction = UnsignedInvokeTransaction()
        signed_invoke_transaction = await self._account_manager.sign_invoke_transaction(
            unsigned_invoke_transaction
        )
        result = await self._client.send_invoke_transaction(signed_invoke_transaction)
        return InvokeOutput()

    async def _translate_calldata_if_necessary(
        self, input_data: InvokeInput
    ) -> CairoDataRepresentation:
        return []
