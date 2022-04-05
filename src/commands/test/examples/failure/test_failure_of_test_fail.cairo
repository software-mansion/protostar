%lang starknet
%builtins pedersen range_check

@external
func test_fail_failure{syscall_ptr : felt*, range_check_ptr}():
    assert 0 = 0
    return ()
end
