%lang starknet

@external
func setup_fuzz_pass() {
    %{ max_examples(5) %}
    %{ given(a = strategy.felts()) %}
    %{ given(b = strategy.felts()) %}
    return ();
}

@external
func test_fuzz_pass{syscall_ptr: felt*, range_check_ptr}(a, b: felt) {
    assert a + b = b + a;
    return ();
}

@external
func setup_fuzz_fails() {
    %{ max_examples(5) %}
    %{ given(a = strategy.felts()) %}
    return ();
}

@external
func test_fuzz_fails{syscall_ptr: felt*, range_check_ptr}(a) {
    // Keep the boundary number low, so that fuzzer shrinking phase does not take a lot of time.
    %{ assert ids.a < 10 %}
    return ();
}
