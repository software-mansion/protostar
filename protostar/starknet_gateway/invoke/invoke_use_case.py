from protostar.starknet_gateway.use_case import DataTransformerProtocol

from .invoke_structs import InvokeInput, InvokeOutput, UnsignedInvokeTransaction
from .invoke_protocols import InvokeAccountManagerProtocol, InvokeClientProtocol


class InvokeUseCase:
    def __init__(
        self,
        client: InvokeClientProtocol,
        account_manager: InvokeAccountManagerProtocol,
        data_transformer: DataTransformerProtocol,
    ) -> None:
        self._client = client
        self._account_manager = account_manager
        self._data_transformer = data_transformer

    async def execute(self, input_data: InvokeInput) -> InvokeOutput:
        cairo_calldata = (
            await self._data_transformer.transform_entrypoint_input_to_cairo(
                address=input_data.address,
                selector=input_data.selector,
                calldata=input_data.calldata,
                abi=input_data.abi,
            )
        )
        unsigned_invoke_tx = UnsignedInvokeTransaction(
            address=input_data.address,
            selector=input_data.selector,
            calldata=cairo_calldata,
            max_fee=input_data.max_fee,
        )
        signed_invoke_tx = await self._account_manager.sign_invoke_transaction(
            unsigned_invoke_tx
        )
        client_response = await self._client.send_invoke_transaction(signed_invoke_tx)
        return InvokeOutput(
            transaction_hash=client_response.transaction_hash,
        )
