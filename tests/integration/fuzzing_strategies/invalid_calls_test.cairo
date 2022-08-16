%lang starknet

@external
func test_unknown_parameter{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{
        given(
            a = strategy.felts(),
            b = strategy.integers(min_value=100, max_value=200),
        )
    %}
    return ()
end

@external
func test_not_strategy_object{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{
        given(a = [])
    %}
    return ()
end

@external
func test_integers_inverted_range{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{ given(a = strategy.integers(200, 100)) %}
    return ()
end
