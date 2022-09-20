%lang starknet

from starkware.cairo.common.math import assert_le

@external
func setup_comparable() {
    %{
        max_examples(10)
        given(a = strategy.felts(comparable=True))
    %}
    return ();
}

@external
func test_comparable{syscall_ptr: felt*, range_check_ptr}(a: felt) {
    assert_le(0, a);
    return ();
}
