%lang starknet

@external
func before{syscall_ptr : felt*, range_check_ptr}():
    %{ test_code["test"] = 111 %}
    return ()
end

@external
func after{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_add
    %{ ids.contract_add = global_storage["test"] %}
    assert contract_add = 111
    return ()
end
