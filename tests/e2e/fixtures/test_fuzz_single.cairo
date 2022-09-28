%lang starknet

from starkware.cairo.common.math import assert_nn

@external
func __setup__() {
    %{ max_examples(1) %}
    return ();
}

@external
func test_fuzz{syscall_ptr: felt*, range_check_ptr}(a, b: felt) {
    %{ print("TESTING STDOUT", ids.a, ids.b) %}
    assert a + b = b + a;
    return ();
}

