from protostar.starknet_gateway.core import DataTransformerProtocol

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
        invoke_tx_to_account = (
            await self._account_manager.prepare_invoke_transaction_to_account(
                unsigned_invoke_tx
            )
        )
        client_response = await self._client.send_invoke_transaction(
            invoke_tx_to_account
        )
        return InvokeOutput(
            transaction_hash=client_response.transaction_hash,
        )

    async def wait_for_acceptance(self, tx_hash: int) -> None:
        await self._client.wait_for_acceptance(tx_hash)
