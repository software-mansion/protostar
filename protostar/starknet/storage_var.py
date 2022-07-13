from typing import List
from starkware.starknet.public.abi import get_storage_var_address
from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash

ADDR_BOUND = 2**251 - 256

def calc_address(variable_name: str, key: List[int]) -> int:
    res = get_storage_var_address(variable_name)
    for i in key:
        res = pedersen_hash(res, i)
    if len(key) > 0:
        res = normalize_address(res)
    return res

def normalize_address(addr: int) -> int:
    return addr if addr < ADDR_BOUND else addr - ADDR_BOUND