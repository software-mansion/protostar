import collections
from typing import Optional

from starkware.python.utils import to_bytes, from_bytes

from .address import Address
from .data_transformer import CairoOrPythonData, CairoData, from_python_transformer
from .cheatable_state import CheatableCachedState


class LocalDataTransformationPolicy:
    def __init__(self, cheatable_cached_state: CheatableCachedState) -> None:
        self._cheatable_cached_state = cheatable_cached_state

    async def transform_calldata_to_cairo_data_by_addr(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        contract_address_int = int(contract_address)
        class_hash = await self._cheatable_cached_state.get_class_hash_at(
            contract_address_int
        )
        return await self._transform_calldata_to_cairo_data(
            class_hash=from_bytes(class_hash, "big"),
            function_name=function_name,
            calldata=calldata,
        )

    async def _transform_calldata_to_cairo_data(
        self,
        class_hash: int,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        if not isinstance(calldata, collections.Mapping):
            return calldata or []
        contract_class = await self._cheatable_cached_state.get_contract_class(
            class_hash=to_bytes(class_hash, 32, "big")
        )
        assert contract_class.abi, f"No abi found for the contract at {class_hash}"
        transformer = from_python_transformer(
            contract_class.abi, function_name, "inputs"
        )
        return transformer(calldata)
