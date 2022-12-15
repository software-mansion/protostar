from typing import Optional

from protostar.protostar_exception import ProtostarException
from protostar.starknet import (
    to_python_transformer,
    from_python_transformer,
    CairoDataRepresentation,
    HumanDataRepresentation,
    Calldata,
    AbiType,
    Address,
    Selector,
)

from .use_case import DataTransformerProtocol
from .abi_resolver import AbiResolver


class DataTransformer(DataTransformerProtocol):
    def __init__(self, abi_resolver: AbiResolver) -> None:
        self._abi_resolver = abi_resolver

    async def transform_calldata_if_necessary(
        self,
        calldata: Optional[Calldata],
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> CairoDataRepresentation:
        if calldata is None:
            return []
        if isinstance(calldata, HumanDataRepresentation):
            abi = abi or await self._resolve_abi_or_fail(address=address)
            transform = from_python_transformer(
                contract_abi=abi, fn_name=str(selector), mode="inputs"
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

    async def try_transforming_entrypoint_output(
        self,
        data: CairoDataRepresentation,
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> Optional[HumanDataRepresentation]:
        abi = abi or await self._abi_resolver.resolve(address)
        if abi is None:
            return None
        transform = to_python_transformer(
            contract_abi=abi,
            fn_name=str(selector),
            mode="outputs",
        )
        return transform(data)


class AbiNotFoundException(ProtostarException):
    def __init__(self, message: str):
        super().__init__(message=message)
