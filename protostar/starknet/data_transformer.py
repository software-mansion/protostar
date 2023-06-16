from typing import Any, Callable, Union
from typing_extensions import Literal

from marshmallow import ValidationError

from starknet_py.serialization import serializer_for_payload
from starknet_py.abi import AbiParsingError, AbiParser

from starkware.starknet.public.abi import AbiType

from protostar.protostar_exception import ProtostarException


class DataTransformerException(ProtostarException):
    pass


CairoData = list[int]
PythonData = dict[str, Any]
CairoOrPythonData = Union[CairoData, PythonData]
FromPythonTransformer = Callable[[PythonData], CairoData]
ToPythonTransformer = Callable[[CairoData], PythonData]


def from_python_transformer(
    contract_abi: AbiType, fn_name: str, mode: Literal["inputs", "outputs"]
) -> FromPythonTransformer:

    try:
        abi = AbiParser(contract_abi).parse()
    except (AbiParsingError, ValidationError) as ex:
        raise DataTransformerException("Invalid ABI") from ex

    try:
        function = abi.functions[fn_name]
    except KeyError as ex:
        raise DataTransformerException(f"Function name `{fn_name}` not in ABI") from ex

    if mode == "inputs":
        serializer = serializer_for_payload(function.inputs)
    else:
        serializer = serializer_for_payload(function.outputs)

    return serializer.serialize


def from_python_events_transformer(
    contract_abi: AbiType, event_name: str
) -> FromPythonTransformer:

    try:
        abi = AbiParser(contract_abi).parse()
    except (AbiParsingError, ValidationError) as ex:
        raise DataTransformerException("Invalid ABI") from ex

    try:
        event = abi.events[event_name]
    except KeyError as ex:
        raise DataTransformerException(f"Event name `{event_name}` not in ABI") from ex

    serializer = serializer_for_payload(event.data)

    return serializer.serialize


def to_python_transformer(
    contract_abi: AbiType, fn_name: str, mode: Literal["inputs", "outputs"]
) -> ToPythonTransformer:
    def transform(data: list[int]):
        try:
            abi = AbiParser(contract_abi).parse()
        except (AbiParsingError, ValidationError) as ex:
            raise DataTransformerException("Invalid ABI") from ex

        try:
            function = abi.functions[fn_name]
        except KeyError as ex:
            raise DataTransformerException(
                f"Function name `{fn_name}` not in ABI"
            ) from ex

        if mode == "inputs":
            serializer = serializer_for_payload(function.inputs)
        else:
            serializer = serializer_for_payload(function.outputs)

        return serializer.deserialize(data).as_dict()

    return transform


def to_python_events_transformer(
    contract_abi: AbiType, event_name: str
) -> ToPythonTransformer:
    def transform(data: list[int]):
        try:
            abi = AbiParser(contract_abi).parse()
        except (AbiParsingError, ValidationError) as ex:
            raise DataTransformerException("Invalid ABI") from ex

        try:
            event = abi.events[event_name]
        except KeyError as ex:
            raise DataTransformerException(
                f"Event name `{event_name}` not in ABI"
            ) from ex

        serializer = serializer_for_payload(event.data)

        return serializer.deserialize(data).as_dict()

    return transform
