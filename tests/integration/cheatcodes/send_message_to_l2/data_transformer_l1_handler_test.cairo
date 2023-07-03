%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func state() -> (res: felt) {
}

@l1_handler
func existing_handler{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    from_address: felt, value: felt
) {
    state.write(value);
    return ();
}

@external
func test_existing_self_l1_handle_call_w_transformer{
    syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr
}() {
    let STATE_AFTER = 'self_l1_handle_call';

    %{ send_message_to_l2("existing_handler", payload={"value": ids.STATE_AFTER}) %}

    let (state_after_l1_msg) = state.read();

    assert state_after_l1_msg = STATE_AFTER;
    return ();
}
