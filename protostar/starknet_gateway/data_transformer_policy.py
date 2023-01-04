from typing import Optional

from protostar.protostar_exception import ProtostarException
from protostar.starknet import (
    to_python_transformer,
    from_python_transformer,
    CairoData,
    PythonData,
    CairoOrPythonData,
    AbiType,
    Address,
    Selector,
)

from .abi_resolver import AbiResolver


class DataTransformerPolicy:
    def __init__(self, abi_resolver: AbiResolver) -> None:
        self._abi_resolver = abi_resolver

    async def transform_entrypoint_input_to_cairo(
        self,
        calldata: Optional[CairoOrPythonData],
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> CairoData:
        if calldata is None:
            return []
        if isinstance(calldata, dict):
            abi = abi or await self.resolve_abi_or_fail(address=address)
            transform = from_python_transformer(
                contract_abi=abi, fn_name=str(selector), mode="inputs"
            )
            return transform(calldata)
        return calldata

    async def resolve_abi_or_fail(self, address: Address):
        abi = await self._abi_resolver.resolve(address)
        if abi is None:
            raise ProtostarException(
                message=(
                    f"Couldn't resolve ABI for address: {address}.\n"
                    "Provide ABI to use data transformer."
                )
            )
        return abi

    async def transform_entrypoint_output_to_human_if_abi_found(
        self,
        data: CairoData,
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> Optional[PythonData]:
        abi = abi or await self._abi_resolver.resolve(address)
        if abi is None:
            return None
        transform = to_python_transformer(
            contract_abi=abi,
            fn_name=str(selector),
            mode="outputs",
        )
        return transform(data)
