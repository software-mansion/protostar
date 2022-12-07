%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

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
