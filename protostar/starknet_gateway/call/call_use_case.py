from typing import Optional

from protostar.starknet import from_python_transformer, to_python_transformer
from protostar.starknet.address import Address

from .call_structs import (
    CallInput,
    CallOutput,
    CallPayload,
    HumanDataRepresentation,
    CairoDataRepresentation,
)
from .call_protocols import ClientProtocol, AbiResolverProtocol
from .call_exceptions import AbiNotFoundException


class CallUseCase:
    def __init__(
        self,
        abi_resolver: AbiResolverProtocol,
        client: ClientProtocol,
    ) -> None:
        self._client = client
        self._abi_resolver = abi_resolver

    async def execute(self, input_data: CallInput) -> CallOutput:
        cairo_calldata = await self._transform_calldata_if_necessary(input_data)
        payload = CallPayload(
            address=input_data.address,
            selector=input_data.selector,
            cairo_calldata=cairo_calldata,
        )
        response = await self._client.send_call(payload)
        response_human_data = await self._try_transforming_response_data(
            response_data=response.cairo_data,
            input_data=input_data,
        )
        return CallOutput(
            cairo_data=response.cairo_data,
            human_data=response_human_data,
        )

    async def _transform_calldata_if_necessary(
        self, input_data: CallInput
    ) -> CairoDataRepresentation:
        calldata = input_data.inputs
        if calldata is None:
            return []
        if isinstance(calldata, HumanDataRepresentation):
            abi = input_data.abi or await self._resolve_abi_or_fail(
                address=input_data.address
            )
            transform = from_python_transformer(
                contract_abi=abi, fn_name=str(input_data.selector), mode="inputs"
            )
            return transform(calldata)
        return calldata

    async def _resolve_abi_or_fail(self, address: Address):
        abi = await self._abi_resolver.resolve(address)
        if abi is None:
            raise AbiNotFoundException(
                message=(
                    f"Couldn't resolve ABI for address: {address}.\n"
                    "Provide ABI to use data transformer."
                )
            )
        return abi

    async def _try_transforming_response_data(
        self, response_data: CairoDataRepresentation, input_data: CallInput
    ) -> Optional[HumanDataRepresentation]:
        abi = input_data.abi or await self._abi_resolver.resolve(input_data.address)
        if abi is None:
            return None
        transform = to_python_transformer(
            contract_abi=abi,
            fn_name=str(input_data.selector),
            mode="outputs",
        )
        return transform(response_data)
