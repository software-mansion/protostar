%lang starknet

@external
func setup_max_examples() {
    %{ given(a = strategy.felts()) %}
    %{ given(b = strategy.felts()) %}
    %{ max_examples(5) %}

    return ();
}

@external
func test_max_examples{syscall_ptr: felt*, range_check_ptr}(a, b: felt) {
    assert a + b = b + a;
    return ();
}
