import json
from typing import List, Dict, Any

from starkware.cairo.lang.compiler.parser import parse_type
from starkware.cairo.lang.compiler.ast.cairo_types import TypePointer, TypeCodeoffset

from protostar.protostar_exception import ProtostarException

from starknet_py.utils.data_transformer.data_transformer import FunctionCallSerializer
from starkware.starknet.public.abi_structs import identifier_manager_from_abi


class InvalidInputException(ProtostarException):
    pass


class JSONParsingErrorException(ProtostarException):
    pass


AbiType = List[Dict[str, Any]]
ConstructorType = Dict[str, Any]


def get_type_size(abi: AbiType, typename: str):
    if typename == "felt":
        return 1
    [type_definition] = [x for x in abi if x["name"] == typename]
    return type_definition["size"]


def get_constructor(abi: AbiType) -> ConstructorType:
    candidates = [x for x in abi if x["type"] == "constructor"]
    if not candidates:
        return {"inputs": [], "outputs": []}
    assert len(candidates) == 1
    return candidates[0]


def get_abi_from_json(compiled_contract_json: str) -> AbiType:
    try:
        abi = json.loads(compiled_contract_json)["abi"]
    except json.decoder.JSONDecodeError as ex:
        raise JSONParsingErrorException(
            "Couldn't parse given contract JSON.", str(ex)
        ) from ex
    except KeyError:
        raise JSONParsingErrorException(
            "No ABI found in the given compiled contract."
        ) from KeyError
    return abi


def validate_deploy_input(compiled_contract_json: str, inputs: List[int]) -> None:
    abi = get_abi_from_json(compiled_contract_json)
    constructor = get_constructor(abi)
    expected_inputs = constructor["inputs"]

    serializer = FunctionCallSerializer(constructor, identifier_manager_from_abi(abi))
    print(serializer.to_python(inputs)._asdict())
    # print(serializer.from_python())

    i = 0
    for expected_input in expected_inputs:

        # print(expected_input["type"], ":", parse_type(expected_input["type"]))

        raw_type_size = get_type_size(abi, expected_input["type"].rstrip("*"))
        if expected_input["type"].endswith("*"):
            size = inputs[i - 1] * raw_type_size
        else:
            size = raw_type_size

        i += size

        if i > len(inputs):
            raise InvalidInputException("Not enough constructor arguments provided.")

    if i != len(inputs):
        raise InvalidInputException(
            f"Too many constructor arguments provided, expected {i} got {len(inputs)}."
        )
