from typing import Any, Callable, Dict, Union

from starknet_py.utils.data_transformer.data_transformer import (
    CairoSerializer,
    CairoData,
)
from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from typing_extensions import Literal

from protostar.utils.abi import find_abi_item


PythonData = Dict[str, Any]
CairoOrPythonData = Union[CairoData, PythonData]
FromPythonTransformer = Callable[[PythonData], CairoData]


def from_python_transformer(
    contract_abi: AbiType,
    fn_name: str,
    mode: Literal["inputs", "outputs"],
) -> FromPythonTransformer:
    fn_abi_item = find_abi_item(contract_abi, fn_name)
    structure_transformer = CairoSerializer(identifier_manager_from_abi(contract_abi))

    def transform(data: PythonData) -> CairoData:
        return structure_transformer.from_python(fn_abi_item[mode], **data)[0]

    return transform


def from_python_events_transformer(
    contract_abi: AbiType,
    event_name: str,
) -> FromPythonTransformer:
    structure_transformer = CairoSerializer(identifier_manager_from_abi(contract_abi))
    event_abi_item = find_abi_item(contract_abi, event_name)

    def transform(data: PythonData) -> CairoData:
        return structure_transformer.from_python(event_abi_item["data"], **data)[0]

    return transform
