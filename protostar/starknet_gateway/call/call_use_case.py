from protostar.starknet import from_python_transformer

from .call_structs import (
    CallInput,
    CallOutput,
    CallClientPayload,
    PythonCalldata,
    CairoCalldata,
)
from .call_protocols import ClientProtocol, AbiResolverProtocol


class CallUseCase:
    def __init__(
        self,
        contract_address_to_abi_converter: AbiResolverProtocol,
        client: ClientProtocol,
    ) -> None:
        self._client = client
        self._contract_address_to_abi_converter = contract_address_to_abi_converter

    async def execute(self, data: CallInput) -> CallOutput:
        cairo_calldata = await self._transform_calldata_if_necessary(data)
        payload = CallClientPayload(
            address=data.address,
            selector=data.selector,
            cairo_calldata=cairo_calldata,
        )
        response = await self._client.call(payload)
        return CallOutput(data=response.data)

    async def _transform_calldata_if_necessary(self, data: CallInput) -> CairoCalldata:
        calldata = data.inputs
        if isinstance(calldata, PythonCalldata):
            abi = await self._contract_address_to_abi_converter.resolve(data.address)
            transform = from_python_transformer(
                contract_abi=abi, fn_name=str(data.selector), mode="inputs"
            )
            return transform(calldata)
        return calldata
