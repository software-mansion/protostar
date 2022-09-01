%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_number

struct Key {
    a: felt,
    b: felt,
}

struct Value {
    a: felt,
    b: felt,
}

@storage_var
func target() -> (res: felt) {
}

@storage_var
func target_map(key: felt) -> (res: felt) {
}

@storage_var
func target_map_struct_key(key: Key) -> (res: felt) {
}

@storage_var
func target_map_struct_val(key: felt) -> (res: Value) {
}

@storage_var
func target_map_complex_key(a: felt, b: felt) -> (res: felt) {
}
