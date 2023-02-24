%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_timestamp, get_block_number

@storage_var
func stored_block_timestamp() -> (res: felt) {
}

@storage_var
func stored_block_number() -> (res: felt) {
}

@view
func stored_block_timestamp_getter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_timestamp) = stored_block_timestamp.read();
    return (res=block_timestamp);
}

@view
func stored_block_number_getter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_number) = stored_block_number.read();
    return (res=block_number);
}

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

@external
func block_timestamp_setter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    let (block_timestamp) = get_block_timestamp();
    stored_block_timestamp.write(block_timestamp);

    return ();
}

@external
func block_number_setter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    let (block_number) = get_block_number();
    stored_block_number.write(block_number);

    return ();
}

@contract_interface
namespace TimestampAndBlockNumberSetter {
    func block_timestamp_setter() {
    }

    func block_number_setter() {
    }
}

@external
func call_block_timestamp_setter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(contract_address: felt) {
    TimestampAndBlockNumberSetter.block_timestamp_setter(contract_address=contract_address);
    return ();
}

@external
func call_block_number_setter{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(contract_address: felt) {
    TimestampAndBlockNumberSetter.block_number_setter(contract_address=contract_address);
    return ();
}
