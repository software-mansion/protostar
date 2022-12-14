from protostar.starknet import Address

from .call_structs import (
    CallInput,
    CallOutput,
    CallClientPayload,
    Calldata,
    PythonCalldata,
    CairoCalldata,
)
from .call_protocols import (
    CallClientProtocol,
    DataTransformerProtocol,
    ContractAddressToAbiConverterProtocol,
)


class CallUseCase:
    def __init__(
        self,
        client: CallClientProtocol,
        contract_address_to_abi_converter: ContractAddressToAbiConverterProtocol,
        data_transformer: DataTransformerProtocol,
    ) -> None:
        self._client = client
        self._contract_address_to_abi_converter = contract_address_to_abi_converter
        self._data_transformer = data_transformer

    async def execute(self, data: CallInput) -> CallOutput:
        cairo_calldata = await self._transform_calldata_if_necessary(
            address=data.address, calldata=data.inputs
        )
        payload = CallClientPayload(
            address=data.address,
            selector=data.selector,
            cairo_calldata=cairo_calldata,
        )
        response = await self._client.call(payload)
        return CallOutput(data=response.data)

    async def _transform_calldata_if_necessary(
        self, address: Address, calldata: Calldata
    ) -> CairoCalldata:
        if isinstance(calldata, PythonCalldata):
            abi = await self._contract_address_to_abi_converter.convert(address)
            return await self._data_transformer.convert_to_cairo_calldata(
                abi=abi, python_calldata=calldata
            )
        return calldata
