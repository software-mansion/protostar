from pathlib import Path
from typing import Any, Callable, Literal, Union

from starkware.starknet.utils.api_utils import cast_to_felts

from protostar.argument_parser import ArgTypeName, map_type_name_to_parser
from protostar.compiler.project_compiler import ContractIdentifier
from protostar.starknet_gateway import (
    SUPPORTED_BLOCK_EXPLORER_NAMES,
    Fee,
    SupportedBlockExplorerName,
    Wei,
)
from protostar.starknet import Address
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.configuration_file import ConfigurationFile

CustomProtostarArgTypeName = Literal[
    "felt",
    "wei",
    "fee",
    "address",
    "class_hash",
    "block_explorer",
    "input",
    "contract_identifier",
]

ProtostarArgTypeName = Union[CustomProtostarArgTypeName, ArgTypeName]

# pylint: disable=too-many-return-statements
def create_map_protostar_type_name_to_parser(configuration_file: ConfigurationFile):
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
        if argument_type == "input":
            return parse_input_arg_type
        if argument_type == "contract_identifier":
            return create_contract_identifier_parser(configuration_file)
        return map_type_name_to_parser(argument_type)

    return map_protostar_type_name_to_parser


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


def create_contract_identifier_parser(configuration_file: ConfigurationFile):
    def parse_contract_identifier(arg: str) -> ContractIdentifier:
        if arg.endswith(".cairo"):
            contract_path = Path(arg)
            if not contract_path.exists():
                raise ValueError(
                    f"The following contract doesn't exist: {contract_path}"
                )
            return contract_path
        contract_names = configuration_file.get_contract_names()
        if arg not in contract_names:
            raise ValueError(f"Unknown contract: {arg}")
        return arg

    return parse_contract_identifier
