from typing import Optional

from protostar.protostar_exception import ProtostarException
from protostar.starknet import (
    DataTransformerService,
    CairoData,
    PythonData,
    CairoOrPythonData,
    Address,
    Selector,
    ContractAbi,
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
        contract_abi: Optional[ContractAbi],
    ) -> CairoData:
        if calldata is None:
            return []
        if isinstance(calldata, dict):
            contract_abi = contract_abi or await self._resolve_abi_or_fail(
                address=address
            )
            data_transformer_service = DataTransformerService(contract_abi)
            return data_transformer_service.transform_entrypoint_inputs_to_cairo_data(
                selector=selector, python_data=calldata
            )
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

    async def transform_entrypoint_output_to_human_if_abi_found(
        self,
        data: CairoData,
        address: Address,
        selector: Selector,
        contract_abi: Optional[ContractAbi],
    ) -> Optional[PythonData]:
        contract_abi = contract_abi or await self._abi_resolver.resolve(address)
        if contract_abi is None:
            return None
        data_transformer_service = DataTransformerService(contract_abi)
        return data_transformer_service.transform_entrypoint_outputs_to_python_data(
            selector=selector, cairo_data=data
        )
