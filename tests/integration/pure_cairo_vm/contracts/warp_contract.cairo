%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_timestamp

@storage_var
func stored_block_timestamp() -> (res: felt) {
}

@view
func get_stored_block_timestamp{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_timestamp) = stored_block_timestamp.read();
    return (res=block_timestamp);
}

@view
func get_syscall_block_timestamp{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_timestamp) = get_block_timestamp();
    return (res=block_timestamp);
}

@external
func set_stored_block_timestamp_to_syscall_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    let (block_timestamp) = get_block_timestamp();
    stored_block_timestamp.write(block_timestamp);

    return ();
}

@contract_interface
namespace TimestampTesterContract {
    func set_stored_block_timestamp_to_syscall_value() {
    }
}

@external
func invoke_set_stored_block_timestamp_to_syscall_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(contract_address: felt) {
    TimestampTesterContract.set_stored_block_timestamp_to_syscall_value(contract_address=contract_address);
    return ();
}
