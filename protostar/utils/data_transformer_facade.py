from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from starknet_py.utils.data_transformer.data_transformer import DataTransformer
from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from typing_extensions import Literal

from protostar.utils.starknet_compilation import StarknetCompiler


class AbiItemNotFoundException(BaseException):
    pass


class PatchedDataTransformer(DataTransformer):
    def patched_from_python(
        self, mode: Literal["inputs", "outputs", "data"], *args, **kwargs
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
    PythonRepresentation = Dict[ArgumentName, SupportedType]
    FromPythonTransformer = Callable[[PythonRepresentation], List[int]]

    def __init__(self, starknet_compiler: StarknetCompiler) -> None:
        self._starknet_compiler = starknet_compiler

    @staticmethod
    def _find_abi(contract_abi: AbiType, name: str) -> Dict:
        for item in contract_abi:
            if item["name"] == name:
                return item
        raise AbiItemNotFoundException(f"Couldn't find '{name}' ABI")

    def build_from_python_transformer(
        self, contract_path: Path, fn_name: str, mode: Literal["inputs", "outputs"]
    ) -> "DataTransformerFacade.FromPythonTransformer":
        contract_abi = self._starknet_compiler.preprocess_contract(contract_path).abi

        fn_abi = self._find_abi(contract_abi, fn_name)

        data_transformer = PatchedDataTransformer(
            fn_abi,
            identifier_manager_from_abi(contract_abi),
        )

        def transform(data: DataTransformerFacade.PythonRepresentation) -> List[int]:
            return data_transformer.patched_from_python(mode, **data)[0]

        return transform

    def build_from_python_events_transformer(
        self, contract_abi: AbiType, event_name: str
    ) -> "DataTransformerFacade.FromPythonTransformer":
        event_abi = self._find_abi(contract_abi, event_name)

        data_transformer = PatchedDataTransformer(
            event_abi,
            identifier_manager_from_abi(contract_abi),
        )

        def transform(data: DataTransformerFacade.PythonRepresentation) -> List[int]:
            return data_transformer.patched_from_python("data", **data)[0]

        return transform
