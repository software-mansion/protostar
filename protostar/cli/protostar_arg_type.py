from typing import Any, Callable, Literal, Union

from starkware.starknet.utils.api_utils import cast_to_felts

from protostar.argument_parser import ArgTypeName
from protostar.argument_parser.arg_type import StandardParserFactory
from protostar.argument_parser.argument_parser_facade import ParserFactory
from protostar.starknet_gateway import (
    SUPPORTED_BLOCK_EXPLORER_NAMES,
    Fee,
    SupportedBlockExplorerName,
    Wei,
)
from protostar.starknet import Address
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.compiler import ContractSourceIdentifierFactory

CustomProtostarArgTypeName = Literal[
    "felt",
    "wei",
    "fee",
    "address",
    "class_hash",
    "block_explorer",
    "input",
    "contract_source_identifier",
]

ProtostarArgTypeName = Union[CustomProtostarArgTypeName, ArgTypeName]


class ProtostarParserFactory(ParserFactory[ProtostarArgTypeName]):  # type: ignore
    def __init__(
        self, contract_source_identifier_factory: ContractSourceIdentifierFactory
    ) -> None:
        self._standard_parser_factory = StandardParserFactory()
        self._contract_source_identifier_factory = contract_source_identifier_factory

    # pylint: disable=too-many-return-statements
    def create(self, argument_type: ProtostarArgTypeName) -> Callable[[str], Any]:
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
        if argument_type == "input":
            return parse_input_arg_type
        if argument_type == "contract_source_identifier":
            return self._contract_source_identifier_factory.create
        return self._standard_parser_factory.create(argument_type)


def parse_felt_arg_type(arg: str) -> int:
    # pylint: disable=unbalanced-tuple-unpacking
    [output] = cast_to_felts([arg])
    return output


def parse_wei_arg_type(arg: str) -> Wei:
    return int(float(arg))


def parse_input_arg_type(arg: str) -> Union[CairoOrPythonData, int]:
    if "=" not in arg:
        return parse_felt_arg_type(arg)
    split_arg = arg.split("=")
    if len(split_arg) != 2:
        raise ValueError("Invalid inputs value, multiple `=` signs are not allowed")
    return {split_arg[0]: parse_felt_arg_type(split_arg[1])}


def parse_fee_arg_type(arg: str) -> Fee:
    if arg == "auto":
        return arg
    return int(arg)


def parse_address_arg_type(arg: str) -> Address:
    return Address.from_user_input(arg)


def parse_hex_or_decimal(arg: str) -> int:
    if arg.startswith("0x"):
        return int(arg, 16)
    return int(arg)


def parse_block_explorer_type(arg: str) -> SupportedBlockExplorerName:
    if arg not in SUPPORTED_BLOCK_EXPLORER_NAMES:
        raise ValueError()
    return arg
