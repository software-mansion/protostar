%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin


@storage_var
func state() -> (res: felt) {
}

@l1_handler
func existing_handler{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr,
    }(from_address: felt, value: felt){
    state.write(value);
    return ();
}

const ALLOWED_L1_SENDER_ADDRESS = 123;

@l1_handler
func existing_handler_verifying_sender_address{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr,
    }(from_address: felt, value: felt){
    assert from_address = ALLOWED_L1_SENDER_ADDRESS;
    state.write(value);
    return ();
}

const PREDEFINED_VALUE = 'somevalue';

@l1_handler
func existing_handler_no_calldata{
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr,
    }(from_address: felt){
    state.write(PREDEFINED_VALUE);
    return ();
}


@external
func test_existing_self_l1_handle_call{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr,
}(){
    let STATE_AFTER = 'self_l1_handle_call';

    %{ send_message_to_l2("existing_handler", payload=[ids.STATE_AFTER]) %}

    let (state_after_l1_msg) = state.read();

    assert state_after_l1_msg = STATE_AFTER;
    return ();
}

@external
func test_existing_self_l1_handle_call_no_calldata{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr,
}(){
    %{ send_message_to_l2("existing_handler_no_calldata") %}

    let (state_after_l1_msg) = state.read();

    assert state_after_l1_msg = PREDEFINED_VALUE;
    return ();
}

@external
func test_existing_self_l1_handle_call_w_transformer{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr,
}(){
    let STATE_AFTER = 'self_l1_handle_call';

    %{ send_message_to_l2("existing_handler", payload={"value": ids.STATE_AFTER}) %}

    let (state_after_l1_msg) = state.read();

    assert state_after_l1_msg = STATE_AFTER;
    return ();
}

@external
func test_non_existing_self_l1_handle_call{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr,
}(){
    let STATE_AFTER = 'self_l1_handle_call';

    %{ send_message_to_l2("non_existing_handler", payload={"value": ids.STATE_AFTER}) %}
    return ();
}

@external
func test_existing_self_l1_handle_call_custom_l1_sender_address{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr,
}(){
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



@contract_interface
namespace ExternalContractInterface {
    func get_state() -> (res: felt) {
    }
}

@external
func test_existing_external_contract_l1_handle_call{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr,
}(){
    alloc_locals;
    local external_contract_address: felt;
    let secret_value = 's3cr3t';
    %{ ids.external_contract_address = deploy_contract("src/main.cairo").contract_address %}
    %{
        send_message_to_l2(
            fn_name="existing_handler",
            from_address=123,
            payload=[ids.secret_value],
            to_address=ids.external_contract_address,
        )
    %}

    let (state) = ExternalContractInterface.get_state(contract_address=external_contract_address);

    assert state = secret_value;
    return ();
}