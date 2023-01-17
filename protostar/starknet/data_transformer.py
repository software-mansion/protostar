from typing import Any, Callable, Dict, Union, Optional
import collections
from typing_extensions import Literal

from starknet_py.utils.data_transformer.data_transformer import (
    CairoSerializer,
    CairoData,
)

from starkware.starknet.public.abi import AbiType
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.contract_class import ContractClass

from protostar.starknet.abi import find_abi_item
from protostar.protostar_exception import ProtostarException
from protostar.starknet.cheater import CheaterException


class DataTransformerException(ProtostarException):
    pass


PythonData = Dict[str, Any]
CairoOrPythonData = Union[CairoData, PythonData]
FromPythonTransformer = Callable[[PythonData], CairoData]
ToPythonTransformer = Callable[[CairoData], PythonData]


def from_python_transformer(
    contract_abi: AbiType, fn_name: str, mode: Literal["inputs", "outputs"]
) -> FromPythonTransformer:
    fn_abi_item = find_abi_item(contract_abi, fn_name)
    structure_transformer = CairoSerializer(identifier_manager_from_abi(contract_abi))

    def transform(data: PythonData) -> CairoData:
        try:
            for data_item_name, data_item_value in data.items():
                for item in fn_abi_item[mode]:
                    if (
                        data_item_name == item["name"]
                        and isinstance(data_item_value, dict)
                        and item["type"] == "felt*"
                    ):
                        raise TypeError(
                            f"invalid type 'dict' for felt* used for argument {data_item_name}"
                        )
            return structure_transformer.from_python(fn_abi_item[mode], **data)[0]
        except (TypeError, ValueError) as ex:
            raise DataTransformerException(str(ex)) from ex

    return transform


def from_python_events_transformer(
    contract_abi: AbiType, event_name: str
) -> FromPythonTransformer:
    event_abi_item = find_abi_item(contract_abi, event_name)
    structure_transformer = CairoSerializer(identifier_manager_from_abi(contract_abi))

    def transform(data: PythonData) -> CairoData:
        try:
            return structure_transformer.from_python(event_abi_item["data"], **data)[0]
        except (TypeError, ValueError) as ex:
            raise DataTransformerException(str(ex)) from ex

    return transform


def to_python_transformer(
    contract_abi: AbiType, fn_name: str, mode: Literal["inputs", "outputs"]
) -> ToPythonTransformer:
    fn_abi_item = find_abi_item(contract_abi, fn_name)
    structure_transformer = CairoSerializer(identifier_manager_from_abi(contract_abi))

    def transform(data: CairoData) -> PythonData:
        try:
            return structure_transformer.to_python(fn_abi_item[mode], data)._asdict()
        except (TypeError, ValueError) as ex:
            raise DataTransformerException(str(ex)) from ex

    return transform


def to_python_events_transformer(
    contract_abi: AbiType, event_name: str
) -> ToPythonTransformer:
    event_abi_item = find_abi_item(contract_abi, event_name)
    structure_transformer = CairoSerializer(identifier_manager_from_abi(contract_abi))

    def transform(data: CairoData) -> PythonData:
        try:
            return structure_transformer.to_python(
                event_abi_item["data"], data
            )._asdict()
        except (TypeError, ValueError) as ex:
            raise DataTransformerException(str(ex)) from ex

    return transform


async def transform_calldata_to_cairo_data(
    contract_class: ContractClass,
    function_name: str,
    calldata: Optional[CairoOrPythonData] = None,
) -> CairoData:
    if isinstance(calldata, collections.Mapping):
        assert contract_class.abi, "Abi required but not found"

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
