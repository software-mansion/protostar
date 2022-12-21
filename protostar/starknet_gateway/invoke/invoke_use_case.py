from typing import TYPE_CHECKING

from .invoke_structs import InvokeInput, InvokeOutput

if TYPE_CHECKING:
    from protostar.starknet_gateway import (
        GatewayFacade,
        AccountManager,
        DataTransformer,
    )


class InvokeUseCase:
    def __init__(
        self,
        client: "GatewayFacade",
        account_manager: "AccountManager",
        data_transformer: "DataTransformer",
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
        payload_to_account_execute = (
            await self._account_manager.prepare_execute_payload_from_unsigned_invoke_tx(
                address=input_data.address,
                selector=input_data.selector,
                calldata=cairo_calldata,
                max_fee=input_data.max_fee,
            )
        )
        response = await self._account_manager.execute(payload_to_account_execute)
        return InvokeOutput(
            transaction_hash=response.transaction_hash,
        )

    async def wait_for_acceptance(self, tx_hash: int) -> None:
        await self._client.wait_for_acceptance(tx_hash)
