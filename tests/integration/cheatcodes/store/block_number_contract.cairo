%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_number

@storage_var
func target() -> (res: felt):
end


@storage_var
func target_map(key: felt) -> (res: felt):
end

@view
func get_value{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        res : felt):
    let (val) = target.read()
    return (val)
end

@view
func get_map_value{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(key : felt) -> (
        res : felt):
    let (val) = target_map.read(key)
    return (val)
end
