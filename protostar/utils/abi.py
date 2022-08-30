import json
from typing import Dict

from starkware.cairo.lang.compiler.ast.cairo_types import CairoType
from starkware.starknet.public.abi import AbiType
from starkware.starknet.testing.contract_utils import parse_arguments


class AbiItemNotFoundException(Exception):
    pass


class AbiNotFoundException(Exception):
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
    for item in contract_abi:
        if item["name"] == name:
            return item
    raise AbiItemNotFoundException(f"Couldn't find '{name}' ABI")


def get_abi_from_compiled_contract(compiled_contract: str) -> AbiType:
    try:
        return json.loads(compiled_contract)["abi"]
    except json.JSONDecodeError as ex:
        raise AbiNotFoundException(
            "Couldn't parse given compiled contract JSON."
        ) from ex
    except KeyError as ex:
        raise AbiNotFoundException(
            "Couldn't find ABI of the compiled contract."
        ) from ex
