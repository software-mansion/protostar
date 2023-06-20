%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func state() -> (res: felt) {
}

@l1_handler
func existing_handler_verifying_sender_address{
    syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr
}(from_address: felt, value: felt) {
    assert from_address = ALLOWED_L1_SENDER_ADDRESS;
    state.write(value);
    return ();
}

@external
func test_existing_self_l1_handle_call_custom_l1_sender_address{
    syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr
}() {
    let STATE_AFTER = 'self_l1_handle_call';

    %{
        send_message_to_l2(
            fn_name="existing_handler_verifying_sender_address",
            payload={"value": ids.STATE_AFTER},
            from_address=ids.ALLOWED_L1_SENDER_ADDRESS,
        )
    %}

    let (state_after_l1_msg) = state.read();
    assert state_after_l1_msg = STATE_AFTER;
    return ();
}
