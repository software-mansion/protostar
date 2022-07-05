from typing import Any, Callable, Dict, List, Tuple

from starknet_py.utils.data_transformer.data_transformer import DataTransformer
from starkware.cairo.lang.compiler.ast.cairo_types import CairoType
from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.testing.contract_utils import parse_arguments
from typing_extensions import Literal

from protostar.utils.starknet_compilation import StarknetCompiler


class AbiItemNotFoundException(Exception):
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
    def _find_abi_item(contract_abi: AbiType, name: str) -> Dict:
        for item in contract_abi:
            if item["name"] == name:
                return item
        raise AbiItemNotFoundException(f"Couldn't find '{name}' ABI")

    @classmethod
    def has_function_parameters(cls, contract_abi: AbiType, name: str) -> bool:
        fn_abi_item = cls._find_abi_item(contract_abi, name)
        if fn_abi_item["type"] != "function":
            raise AbiItemNotFoundException(f"ABI item '{name}' not a function.")

        return bool(fn_abi_item["inputs"])

    @classmethod
    def get_function_parameters(
        cls, contract_abi: AbiType, name: str
    ) -> Dict[str, CairoType]:
        fn_abi_item = cls._find_abi_item(contract_abi, name)
        if fn_abi_item["type"] != "function":
            raise AbiItemNotFoundException(f"ABI item '{name}' not a function.")

        names, types = parse_arguments(fn_abi_item["inputs"])
        assert len(names) == len(types)
        return dict(zip(names, types))

    def build_from_python_transformer(
        self, contract_abi: AbiType, fn_name: str, mode: Literal["inputs", "outputs"]
    ) -> "DataTransformerFacade.FromPythonTransformer":

        fn_abi_item = self._find_abi_item(contract_abi, fn_name)

        data_transformer = PatchedDataTransformer(
            fn_abi_item,
            identifier_manager_from_abi(contract_abi),
        )

        def transform(data: DataTransformerFacade.PythonRepresentation) -> List[int]:
            return data_transformer.patched_from_python(mode, **data)[0]

        return transform

    def build_from_python_events_transformer(
        self, contract_abi: AbiType, event_name: str
    ) -> "DataTransformerFacade.FromPythonTransformer":
        event_abi_item = self._find_abi_item(contract_abi, event_name)

        data_transformer = PatchedDataTransformer(
            event_abi_item,
            identifier_manager_from_abi(contract_abi),
        )

        def transform(data: DataTransformerFacade.PythonRepresentation) -> List[int]:
            return data_transformer.patched_from_python("data", **data)[0]

        return transform
