import copy
import collections

from abc import ABC
from typing import Optional, TYPE_CHECKING
from typing_extensions import Self

from starkware.python.utils import to_bytes, from_bytes

from protostar.starknet.cheater import Cheater, CheaterException
from protostar.starknet.address import Address
from protostar.starknet.data_transformer import (
    DataTransformerException,
    CairoOrPythonData,
    CairoData,
    from_python_transformer,
)

if TYPE_CHECKING:
    from protostar.starknet.cheatable_cached_state import CheatableCachedState


class StatefulCheater(Cheater, ABC):
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    def copy(self) -> Self:
        return copy.copy(self)

    def apply(self, parent: Self) -> None:
        pass

    async def _transform_calldata_to_cairo_data_by_addr(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        contract_address_int = int(contract_address)
        class_hash = await self.cheatable_state.get_class_hash_at(contract_address_int)
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
        if isinstance(calldata, collections.Mapping):
            contract_class = await self.cheatable_state.get_contract_class(
                class_hash=to_bytes(class_hash, 32, "big")
            )
            assert contract_class.abi, f"No abi found for the contract at {class_hash}"

            transformer = from_python_transformer(
                contract_class.abi, function_name, "inputs"
            )
            try:
                return transformer(calldata)
            except DataTransformerException as dt_exc:
                raise CheaterException(
                    f"There was an error while parsing the arguments for the function {function_name}:\n"
                    + f"{dt_exc.message}",
                ) from dt_exc
        return calldata or []
