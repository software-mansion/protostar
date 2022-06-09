from pathlib import Path
from typing import List

from starknet_py.utils.data_transformer.data_transformer import (
    ABIFunctionEntry,
    DataTransformer,
)
from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from protostar.utils.starknet_compilation import StarknetCompiler


class FunctionNotFoundException(BaseException):
    pass


class DataTransformerFacade:
    @classmethod
    def from_contract_path(
        cls, path: Path, starknet_compiler: StarknetCompiler
    ) -> "DataTransformerFacade":
        preprocessed = starknet_compiler.preprocess_contract(path)
        return cls(preprocessed.abi)

    def __init__(self, contract_abi: AbiType) -> None:
        self._contract_abi = contract_abi
        self._identifier_manager = identifier_manager_from_abi(contract_abi)

    def _get_function_abi(self, fn_name: str) -> ABIFunctionEntry:
        for item in self._contract_abi:
            if (item["type"] == "function" or item["type"] == "constructor") and item[
                "name"
            ] == fn_name:
                return item
        raise FunctionNotFoundException(f"Couldn't find a function {fn_name}")

    def from_python(self, fn_name: str, *args, **kwargs) -> List[int]:
        data_transformer = DataTransformer(
            self._get_function_abi(fn_name),
            identifier_manager_from_abi(self._contract_abi),
        )
        return data_transformer.from_python(args, kwargs)[0]
