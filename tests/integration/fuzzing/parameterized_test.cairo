%lang starknet

from starkware.cairo.common.math import assert_le

////////// no data - broken test

@external
func setup_no_data() {
    return ();
}

@external
func test_no_data{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    return ();
}

////////// only examples

@external
func setup_only_examples() {
    %{
        example(a=3, b=4)
        example(b=6, a=5)
    %}
    return ();
}

@external
func test_only_examples{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    assert_le(0, a);
    assert_le(0, b);
    assert_le(a, b);
    return ();
}

////////// only given

@external
func setup_only_given() {
    %{
        given(a = strategy.integers(10, 20), b = strategy.integers(30, 40))
    %}
    return ();
}

@external
func test_only_given{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    assert_le(0, a);
    assert_le(0, b);
    assert_le(a, b);
    return ();
}

////////// given and examples

@external
func setup_given_and_examples() {
    %{
        max_examples(5)

        example(a=3, b=4)
        given(a = strategy.integers(10, 20), b = strategy.integers(30, 40))
        example(b=6, a=5)
    %}
    return ();
}

@external
func test_given_and_examples{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    assert_le(0, a);
    assert_le(0, b);
    assert_le(a, b);
    return ();
}

////////// check exact example

@external
func setup_check_exact_example() {
    %{
        example(a=11, b=17)
    %}
    return ();
}

@external
func test_check_exact_example{syscall_ptr: felt*, range_check_ptr}(a: felt, b: felt) {
    %{
        assert ids.a == 11
        assert ids.b == 17
    %}
    return ();
}

