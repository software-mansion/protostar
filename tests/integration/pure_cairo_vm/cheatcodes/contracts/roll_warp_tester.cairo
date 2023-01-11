%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_timestamp, get_block_number

@view
func timestamp_getter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_timestamp) = get_block_timestamp();
    return (res=block_timestamp);
}

@view
func block_number_getter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_number) = get_block_number();
    return (res=block_number);
}