%lang starknet

from starkware.cairo.common.math import assert_le

@external
func setup_rc_bound() {
    %{
        max_examples(10)
        given(a = strategy.felts(rc_bound=True))
    %}
    return ();
}

@external
func test_rc_bound{syscall_ptr: felt*, range_check_ptr}(a: felt) {
    assert_le(0, a);
    return ();
}
