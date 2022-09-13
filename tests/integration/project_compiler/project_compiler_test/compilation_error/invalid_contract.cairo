%lang starknet

@view
func use_not_whitelisted_hint{syscall_ptr: felt*}(contract_address: felt) {
    tempvar x;
    %{ ids.x = 42 %}
    return ();
}
