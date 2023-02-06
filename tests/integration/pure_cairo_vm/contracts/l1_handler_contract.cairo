%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_timestamp

@storage_var
func state() -> (res: felt) {
}

@event
func fake_event() {
}

@l1_handler
func existing_handler{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    from_address: felt, value: felt
) {
    fake_event.emit();
    state.write(value);
    return ();
}

@view
func get_state{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = state.read();
    return (res=res);
}

@l1_handler
func on_l1_msg_set_block_timestamp{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    from_address: felt
) {
    let (block_timestamp) = get_block_timestamp();
    state.write(block_timestamp);
    return ();
}

@contract_interface
namespace TimestampTesterContract {
    func block_timestamp_setter() -> (res: felt) {
    }
}

@l1_handler
func call_set_block_timestamp{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    from_address: felt, target_address: felt
) {
    let (block_timestamp) = TimestampTesterContract.block_timestamp_setter(target_address);
    state.write(block_timestamp);
    return ();
}
