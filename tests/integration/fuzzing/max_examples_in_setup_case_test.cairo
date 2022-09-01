%lang starknet

@external
func __setup__() {
    // Setup case should override this.
    %{ max_examples(7) %}
    return ();
}

@external
func setup_max_examples() {
    %{ max_examples(5) %}
    return ();
}

@external
func test_max_examples{syscall_ptr: felt*, range_check_ptr}(a, b: felt) {
    assert a + b = b + a;
    return ();
}
