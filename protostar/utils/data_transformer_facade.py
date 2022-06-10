from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from starknet_py.utils.data_transformer.data_transformer import (
    ABIFunctionEntry,
    DataTransformer,
)
from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from typing_extensions import Literal

from protostar.utils.starknet_compilation import StarknetCompiler


class FunctionNotFoundException(BaseException):
    pass


class PatchedDataTransformer(DataTransformer):
    def patched_from_python(
        self, mode: Literal["inputs", "outputs"], *args, **kwargs
    ) -> Tuple[List[int], Dict[str, List[int]]]:
        """
        Transforms params into Cairo representation.
        :return: tuple (full calldata, dict with all arguments with their Cairo representation)
        """
        type_by_name = self._abi_to_types(self.abi[mode])

        named_arguments = {**kwargs}

        if len(args) > len(type_by_name):
            raise TypeError(
                f"Provided {len(args)} positional arguments, {len(type_by_name)} possible."
            )

        # Assign args to named arguments
        for arg, input_name in zip(args, type_by_name.keys()):
            if input_name in named_arguments:
                raise TypeError(
                    f"Both positional and named argument provided for {input_name}."
                )
            named_arguments[input_name] = arg

        all_params: Dict[str, List[int]] = {}
        calldata: List[int] = []
        for name, cairo_type in type_by_name.items():
            if name not in named_arguments:
                raise TypeError(f"'{name}' was not provided")

            values = self.resolve_type(cairo_type).from_python(
                cairo_type, name, named_arguments[name]
            )

            all_params[name] = values

            calldata.extend(values)

        return calldata, all_params


class DataTransformerFacade:
    ArgumentName = str
    SupportedType = Any

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
        raise FunctionNotFoundException(f"Couldn't find a function '{fn_name}'")

    def build_from_python_transformer(
        self, fn_name: str, mode: Literal["inputs", "outputs"]
    ) -> Callable[[Dict[ArgumentName, SupportedType]], List[int]]:
        fn_abi = self._get_function_abi(fn_name)

        data_transformer = PatchedDataTransformer(
            fn_abi,
            identifier_manager_from_abi(self._contract_abi),
        )

        def transform(
            data: Dict[
                DataTransformerFacade.ArgumentName,
                DataTransformerFacade.SupportedType,
            ]
        ) -> List[int]:
            return data_transformer.patched_from_python(mode, **data)[0]

        return transform
