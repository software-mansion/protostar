from typing import Any, Callable, Union
from typing_extensions import Literal

from marshmallow import ValidationError

from starknet_py.serialization import serializer_for_payload, CairoSerializerException
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
    def transform(data: PythonData):
        try:
            abi = AbiParser(contract_abi).parse()
        except (AbiParsingError, ValidationError) as ex:
            raise DataTransformerException("Invalid ABI") from ex

        try:
            if fn_name == "constructor":
                function = abi.constructor
                if function is None:
                    raise DataTransformerException("Constructor not in ABI")
            else:
                function = abi.functions[fn_name]
        except KeyError as ex:
            raise DataTransformerException(
                f"Function name `{fn_name}` not in ABI"
            ) from ex

        if mode == "inputs":
            serializer = serializer_for_payload(function.inputs)
        else:
            serializer = serializer_for_payload(function.outputs)

        try:
            return serializer.serialize(data)
        except (CairoSerializerException, KeyError) as ex:
            raise DataTransformerException("Data transformer error") from ex

    return transform


def from_python_events_transformer(
    contract_abi: AbiType, event_name: str
) -> FromPythonTransformer:
    def transform(data: PythonData):
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

        try:
            return serializer.serialize(data)
        except (CairoSerializerException, KeyError) as ex:
            raise DataTransformerException("Data transformer error") from ex

    return transform


def to_python_transformer(
    contract_abi: AbiType, fn_name: str, mode: Literal["inputs", "outputs"]
) -> ToPythonTransformer:
    def transform(data: CairoData):
        try:
            abi = AbiParser(contract_abi).parse()
        except (AbiParsingError, ValidationError) as ex:
            raise DataTransformerException("Invalid ABI") from ex

        try:
            if fn_name == "constructor":
                function = abi.constructor
                if function is None:
                    raise DataTransformerException("Constructor not in ABI")
            else:
                function = abi.functions[fn_name]
        except KeyError as ex:
            raise DataTransformerException(
                f"Function name `{fn_name}` not in ABI"
            ) from ex

        if mode == "inputs":
            serializer = serializer_for_payload(function.inputs)
        else:
            serializer = serializer_for_payload(function.outputs)

        try:
            return serializer.deserialize(data).as_dict()
        except CairoSerializerException as ex:
            raise DataTransformerException("Data transformer error") from ex

    return transform


def to_python_events_transformer(
    contract_abi: AbiType, event_name: str
) -> ToPythonTransformer:
    def transform(data: CairoData):
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

        try:
            return serializer.deserialize(data).as_dict()
        except CairoSerializerException as ex:
            raise DataTransformerException("Data transformer error") from ex

    return transform
