%lang starknet

@external
func test_reject_not_fuzz{syscall_ptr : felt*, range_check_ptr}():
    %{ reject() %}
    return ()
end

@external
func test_assume_not_fuzz{syscall_ptr : felt*, range_check_ptr}():
    %{ assume(True) %}
    return ()
end

@external
func test_passed_assume{syscall_ptr : felt*, range_check_ptr}(a):
    %{ assume(True) %}
    return ()
end
