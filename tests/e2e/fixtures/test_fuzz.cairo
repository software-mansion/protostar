%lang starknet

from starkware.cairo.common.math import assert_nn

@external
func setup_fuzz() {
    %{ given(a = strategy.felts()) %}
    %{ given(b = strategy.felts()) %}
    return ();
}

@external
func test_fuzz{syscall_ptr: felt*, range_check_ptr}(a, b: felt) {
    %{ print("TESTING STDOUT", ids.a) %}
    assert a + b = b + a;
    return ();
}

@external
func setup_fails_if_big_single_input() {
    %{ given(x = strategy.felts()) %}
    return ();
}

@external
func test_fails_if_big_single_input{syscall_ptr: felt*, range_check_ptr}(x) {
    assert_nn(x);
    return ();
}

@external
func setup_fails_if_big_many_inputs() {
    %{ given(a = strategy.felts()) %}
    %{ given(b = strategy.felts()) %}
    %{ given(c = strategy.felts()) %}
    return ();
}

@external
func test_fails_if_big_many_inputs{syscall_ptr: felt*, range_check_ptr}(a, b, c) {
    assert_nn(a);
    return ();
}
