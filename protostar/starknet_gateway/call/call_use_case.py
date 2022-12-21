from typing import TYPE_CHECKING

from .call_structs import CallInput, CallOutput

if TYPE_CHECKING:
    from protostar.starknet_gateway import GatewayFacade, DataTransformer


class CallUseCase:
    def __init__(
        self,
        gateway_facade: "GatewayFacade",
        data_transformer: "DataTransformer",
    ) -> None:
        self._gateway_facade = gateway_facade
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
        response_cairo_data = await self._gateway_facade.send_call(
            address=input_data.address,
            selector=input_data.selector,
            cairo_calldata=cairo_calldata,
        )
        response_human_data = await self._data_transformer.transform_entrypoint_output_to_human_if_abi_found(
            data=response_cairo_data,
            address=input_data.address,
            selector=input_data.selector,
            abi=input_data.abi,
        )
        return CallOutput(
            cairo_data=response_cairo_data,
            human_data=response_human_data,
        )
