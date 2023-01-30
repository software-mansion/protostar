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

@view
func get_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (val) = target.read();
    return (val,);
}

@view
func get_map_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(key: felt) -> (
    res: felt
) {
    let (val) = target_map.read(key);
    return (val,);
}

@view
func get_map_value_struct_key{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    key: Key
) -> (res: felt) {
    let (val) = target_map_struct_key.read(key);
    return (val,);
}

@view
func get_map_value_struct_val{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    key: felt
) -> (res: Value) {
    let (val) = target_map_struct_val.read(key);
    return (val,);
}

@view
func get_map_value_complex_key{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) -> (res: felt) {
    let (val) = target_map_complex_key.read(a, b);
    return (val,);
}
