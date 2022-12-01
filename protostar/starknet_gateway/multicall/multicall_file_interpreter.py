from typing import Literal, TypeVar, Union, cast

import tomlkit as toml
from typing_extensions import TypedDict
from tomlkit.items import AoT

from protostar.starknet import Address, RawAddress, Selector

from .multicall_structs import Call, InvokeCall, DeployCall, Identifier

Variable = str


DeployRawCall = TypedDict(
    "DeployRawCall",
    {
        "type": Literal["deploy"],
        "id": str,
        "calldata": list[Union[int, Variable]],
        "class-hash": int,
    },
)

InvokeRawCall = TypedDict(
    "InvokeRawCall",
    {
        "type": Literal["invoke"],
        "calldata": list[Union[int, Variable]],
        "contract-address": Union[RawAddress, Variable],
        "entrypoint-name": str,
    },
)


RawCall = Union[DeployRawCall, InvokeRawCall]


def interpret_multicall_file_content(toml_content: str) -> list[Call]:
    raw_calls = parse_toml_multicall(toml_content)
    return [map_raw_call_to_call_base(raw_call) for raw_call in raw_calls]


def parse_toml_multicall(toml_content: str) -> list[RawCall]:
    doc = toml.loads(toml_content)
    call_aot = doc.get("call")
    assert isinstance(call_aot, AoT)
    return cast(list[RawCall], call_aot.value)


def map_raw_call_to_call_base(raw_call: RawCall) -> Call:
    if raw_call["type"] == "invoke":
        address = parse_potential_identifier(raw_call["contract-address"])
        if not isinstance(address, Identifier):
            address = Address.from_user_input(address)
        return InvokeCall(
            address=address,
            calldata=[parse_potential_identifier(i) for i in raw_call["calldata"]],
            selector=Selector(raw_call["entrypoint-name"]),
        )
    if raw_call["type"] == "deploy":
        return DeployCall(
            address_alias=Identifier(raw_call["id"]),
            calldata=[parse_potential_identifier(i) for i in raw_call["calldata"]],
            class_hash=raw_call["class-hash"],
        )
    assert False, "Unknown call type"


T = TypeVar("T")


def parse_potential_identifier(value: Union[T, str]) -> Union[T, Identifier]:
    if isinstance(value, str):
        value.startswith("$")
        return Identifier(value[1:])
    return value
