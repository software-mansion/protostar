from typing import TYPE_CHECKING

from protostar.starknet_gateway.core import DataTransformerProtocol

from .call_structs import CallInput, CallOutput, CallPayload

if TYPE_CHECKING:
    from protostar.starknet_gateway import GatewayFacade


class CallUseCase:
    def __init__(
        self,
        client: "GatewayFacade",
        data_transformer: DataTransformerProtocol,
    ) -> None:
        self._client = client
        self._data_transformer = data_transformer

    async def execute(self, input_data: CallInput) -> CallOutput:
        cairo_calldata = (
            await self._data_transformer.transform_entrypoint_input_to_cairo(
                address=input_data.address,
                selector=input_data.selector,
                calldata=input_data.inputs,
                abi=input_data.abi,
            )
        )
        payload = CallPayload(
            address=input_data.address,
            selector=input_data.selector,
            cairo_calldata=cairo_calldata,
        )
        response = await self._client.send_call(payload)
        response_human_data = (
            await self._data_transformer.try_transforming_entrypoint_output_to_human(
                data=response.cairo_data,
                address=input_data.address,
                selector=input_data.selector,
                abi=input_data.abi,
            )
        )
        return CallOutput(
            cairo_data=response.cairo_data,
            human_data=response_human_data,
        )
