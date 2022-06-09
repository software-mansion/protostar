from typing import List

from starknet_py.utils.data_transformer.data_transformer import (
    ABIFunctionEntry,
    DataTransformer,
)
from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi


class DataTransformerFacade:
    def __init__(self, contract_abi: AbiType, function_abi: ABIFunctionEntry) -> None:
        self._identifier_manager = identifier_manager_from_abi(contract_abi)
        self._data_transformer = DataTransformer(
            function_abi, identifier_manager_from_abi(contract_abi)
        )

    def from_python(self, *args, **kwargs) -> List[int]:
        return self._data_transformer.from_python(args, kwargs)[0]
