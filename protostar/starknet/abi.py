import json
from pathlib import Path
from typing import Any, Dict

from starkware.cairo.lang.compiler.ast.cairo_types import CairoType
from starkware.starknet.public.abi import AbiType
from starkware.starknet.testing.contract_utils import parse_arguments

from protostar.protostar_exception import ProtostarException


class AbiItemNotFoundException(ProtostarException):
    pass


def has_function_parameters(contract_abi: AbiType, name: str) -> bool:
    fn_abi_item = find_abi_item(contract_abi, name)
    if fn_abi_item["type"] != "function":
        raise AbiItemNotFoundException(f"ABI item '{name}' not a function.")

    return bool(fn_abi_item["inputs"])


def get_function_parameters(contract_abi: AbiType, name: str) -> Dict[str, CairoType]:
    fn_abi_item = find_abi_item(contract_abi, name)
    if fn_abi_item["type"] != "function":
        raise AbiItemNotFoundException(f"ABI item '{name}' not a function.")

    names, types = parse_arguments(fn_abi_item["inputs"])
    assert len(names) == len(types)
    return dict(zip(names, types))


def find_abi_item(contract_abi: AbiType, name: str) -> Dict:
    try:
        for item in contract_abi:
            if item["name"] == name:
                return item
        raise AbiItemNotFoundException(f"Couldn't find '{name}' ABI")
    except TypeError as ex:
        raise AbiItemNotFoundException(str(ex)) from ex


def has_abi_item(contract_abi: AbiType, name: str) -> bool:
    for item in contract_abi:
        if item["name"] == name:
            return True
    return False


def load_abi(abi_path: Path) -> AbiType:
    assert abi_path.suffix == ".json"
    potential_abi = json.loads(abi_path.read_text())
    panic_if_invalid_abi(potential_abi)
    return potential_abi


def panic_if_invalid_abi(abi: Any):
    if not isinstance(abi, list):
        raise ProtostarException("Invalid ABI.")
