%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_number

struct Key:
    member a : felt
    member b : felt
end

struct Value:
    member a : felt
    member b : felt
end

@storage_var
func target() -> (res: felt):
end

@storage_var
func target_map(key: felt) -> (res: felt):
end

@storage_var
func target_map_struct_key(key: Key) -> (res: felt):
end

@storage_var
func target_map_struct_val(key: felt) -> (res: Value):
end

@storage_var
func target_map_complex_key(a: felt, b: felt) -> (res: felt):
end


