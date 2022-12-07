%lang starknet

@external
func test_reject_not_fuzz{syscall_ptr: felt*, range_check_ptr}() {
    %{ reject() %}
    return ();
}

@external
func test_assume_not_fuzz{syscall_ptr: felt*, range_check_ptr}() {
    %{ assume(True) %}
    return ();
}

@external
func setup_passed_assume() {
    %{ given(a = strategy.felts()) %}
    return ();
}

@external
func test_passed_assume{syscall_ptr: felt*, range_check_ptr}(a) {
    %{ assume(True) %}
    return ();
}
