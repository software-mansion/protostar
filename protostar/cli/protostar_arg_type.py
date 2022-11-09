from typing import Any, Callable, Literal, Union

from starkware.starknet.utils.api_utils import cast_to_felts

from protostar.argument_parser import ArgTypeName, map_type_name_to_parser
from protostar.starknet_gateway import (
    SUPPORTED_BLOCK_EXPLORER_NAMES,
    Fee,
    SupportedBlockExplorerName,
    Wei,
)

CustomProtostarArgTypeName = Literal[
    "felt", "wei", "fee", "address", "class_hash", "block_explorer"
]

ProtostarArgTypeName = Union[CustomProtostarArgTypeName, ArgTypeName]

# pylint: disable=too-many-return-statements
def map_protostar_type_name_to_parser(
    argument_type: ProtostarArgTypeName,
) -> Callable[[str], Any]:
    if argument_type == "felt":
        return parse_felt_arg_type
    if argument_type == "fee":
        return parse_fee_arg_type
    if argument_type == "address":
        return parse_hex_or_decimal
    if argument_type == "class_hash":
        return parse_hex_or_decimal
    if argument_type == "wei":
        return parse_wei_arg_type
    if argument_type == "block_explorer":
        return parse_block_explorer_type
    return map_type_name_to_parser(argument_type)


def parse_felt_arg_type(arg: str) -> int:
    # pylint: disable=unbalanced-tuple-unpacking
    [output] = cast_to_felts([arg])
    return output


def parse_wei_arg_type(arg: str) -> Wei:
    return int(float(arg))


def parse_fee_arg_type(arg: str) -> Fee:
    if arg == "auto":
        return arg
    return int(arg)


def parse_hex_or_decimal(arg: str) -> int:
    if arg.startswith("0x"):
        return int(arg, 16)
    return int(arg)


def parse_block_explorer_type(arg: str) -> SupportedBlockExplorerName:
    assert arg in SUPPORTED_BLOCK_EXPLORER_NAMES
    return arg
