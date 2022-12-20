from typing import Optional, TYPE_CHECKING

from protostar.starknet import from_python_transformer, to_python_transformer
from protostar.starknet.address import Address
from protostar.protostar_exception import ProtostarException

from .call_structs import (
    CallInput,
    CallOutput,
    HumanDataRepresentation,
    CairoDataRepresentation,
)

if TYPE_CHECKING:
    from protostar.starknet_gateway import GatewayFacade, AbiResolver


class CallUseCase:
    def __init__(
        self,
        abi_resolver: "AbiResolver",
        client: "GatewayFacade",
    ) -> None:
        self._client = client
        self._abi_resolver = abi_resolver

    async def execute(self, input_data: CallInput) -> CallOutput:
        cairo_calldata = await self._transform_calldata_if_necessary(input_data)
        response_data = await self._client.send_call(
            address=input_data.address,
            selector=input_data.selector,
            cairo_calldata=cairo_calldata,
        )
        response_human_data = await self._try_transforming_response_data(
            response_data=response_data,
            input_data=input_data,
        )
        return CallOutput(
            cairo_data=response_data,
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
            raise ProtostarException(
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
