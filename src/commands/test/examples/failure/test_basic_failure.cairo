%lang starknet
%builtins pedersen range_check

@external
func test_failure{syscall_ptr : felt*, range_check_ptr}(contract_address: felt):
    assert 1=0
    return ()
end
