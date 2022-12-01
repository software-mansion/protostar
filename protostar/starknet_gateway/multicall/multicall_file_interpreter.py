from dataclasses import dataclass
from typing import Literal, cast

import tomlkit as toml
from typing_extensions import TypedDict
from tomlkit.items import AoT

from .multicall_structs import CallBase, InvokeCall, DeployCall


@dataclass
class RawCall(TypedDict):
    type: Literal["invoke", "deploy"]


@dataclass
class DeployRawCall(RawCall):
    id: str


@dataclass
class InvokeRawCall(RawCall):
    pass


def interpret_multicall_file_content(toml_content: str) -> list[CallBase]:
    raw_calls = parse_toml_multicall(toml_content)
    return []


def parse_toml_multicall(toml_content: str) -> list[RawCall]:
    doc = toml.loads(toml_content)
    call_aot = doc.get("call")
    assert isinstance(call_aot, AoT)
    return cast(list[RawCall], call_aot.value)


def map_raw_call_to_call_base(raw_call: RawCall) -> CallBase:
    if raw_call["type"] == "invoke":
        return InvokeCall(address=Address())
    if raw_call["type"] == "deploy":
        return DeployCall()
    assert False, "Unknown call type"
