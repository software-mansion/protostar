from typing import Any, Callable, Literal, Union

from starkware.starknet.utils.api_utils import cast_to_felts

from protostar.starknet_gateway import Fee

from .arg_type import ArgTypeName, map_type_name_to_parser

ProtostarArgTypeName = Literal[
    "felt",
    "fee",
]


def map_protostar_type_name_to_parser(
    argument_type: Union[ProtostarArgTypeName, ArgTypeName]
) -> Callable[[str], Any]:
    type_name_to_parser_mapping: dict[ProtostarArgTypeName, Callable[[str], Any]] = {
        "felt": parse_felt_arg_type,
        "fee": parse_fee_arg_type,
    }
    if argument_type in type_name_to_parser_mapping:
        return type_name_to_parser_mapping[argument_type]
    return map_type_name_to_parser(argument_type)


def parse_felt_arg_type(arg: str) -> int:
    # pylint: disable=unbalanced-tuple-unpacking
    [output] = cast_to_felts([arg])
    return output


def parse_fee_arg_type(arg: str) -> Fee:
    if arg == "auto":
        return arg
    return int(arg)
