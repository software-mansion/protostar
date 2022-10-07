%lang starknet

from starkware.cairo.common.math import assert_le

@external
func setup_examples() {
    %{
        max_examples(5)
        # todo test no example
        example(1, 2)
        example(2, 3)
        example(a=3, b=4)
        example(b=6, a=5)
        given(a = strategy.integers(15, 20), b = strategy.integers(10, 14))
    %}
    return ();
}

@external
func test_examples{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    assert_le(0, a);
    assert_le(0, b);
    return ();
}

