%lang starknet

@external
func setup_correct_short_string() {
    %{ given(value=strategy.short_strings()) %}
    return ();
}

@external
func test_correct_short_string{syscall_ptr: felt*, range_check_ptr}(value: felt) {
    %{
        max_short_string_int_value = int('0x' + 'ff'*31, 16)
        assert ids.value >= 0
        assert ids.value <= max_short_string_int_value
    %}
    return ();
}
