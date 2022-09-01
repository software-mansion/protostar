%lang starknet

from starkware.cairo.common.math import assert_le

@external
func __setup__() {
    %{ max_examples(5) %}
    return ();
}

@external
func test_integers{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    %{
        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    assert_le(a, b);
    return ();
}
