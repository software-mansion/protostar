%lang starknet

@external
func setup_correct_short_string() {
    %{ given(value=strategy.short_strings()) %}
    return ();
}

@external
func test_correct_short_string{syscall_ptr: felt*, range_check_ptr}(value: felt) {
    %{ assert 0 <= ids.value %}
    return ();
}
