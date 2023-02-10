from typing import TYPE_CHECKING

from .invoke_structs import InvokeInput, InvokeOutput

if TYPE_CHECKING:
    from protostar.starknet_gateway import (
        GatewayFacade,
        AccountManager,
        DataTransformerPolicy,
    )


class InvokeUseCase:
    def __init__(
        self,
        client: "GatewayFacade",
        account_manager: "AccountManager",
        data_transformer_policy: "DataTransformerPolicy",
    ) -> None:
        self._client = client
        self._account_manager = account_manager
        self._data_transformer_policy = data_transformer_policy

    async def execute(self, input_data: InvokeInput) -> InvokeOutput:
        cairo_calldata = (
            await self._data_transformer_policy.transform_entrypoint_input_to_cairo(
                address=input_data.address,
                selector=input_data.selector,
                calldata=input_data.calldata,
                contract_abi=input_data.contract_abi,
            )
        )
        prepared_invoke_tx = await self._account_manager.prepare_invoke_transaction(
            address=input_data.address,
            selector=input_data.selector,
            calldata=cairo_calldata,
            max_fee=input_data.max_fee,
        )
        transaction_hash = await self._account_manager.execute(prepared_invoke_tx)
        return InvokeOutput(
            transaction_hash=transaction_hash,
        )

    async def wait_for_acceptance(self, tx_hash: int) -> None:
        await self._client.wait_for_acceptance(tx_hash)
