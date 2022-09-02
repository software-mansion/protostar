%lang starknet

@external
func __setup__():
    %{ max_examples(3) %}
    return ()
end

@external
func setup_unknown_parameter():
    %{
        given(
            a = strategy.felts(),
            b = strategy.integers(min_value=100, max_value=200),
        )
    %}
    return ()
end

@external
func test_unknown_parameter(a : felt):
    return ()
end

@external
func setup_not_strategy_object():
    %{ given(a = []) %}
    return ()
end

@external
func test_not_strategy_object(a : felt, b : felt):
    return ()
end

@external
func setup_repeated_parameter():
    %{ given(a = strategy.felts()) %}
    %{ given(a = strategy.felts()) %}
    return ()
end

@external
func test_repeated_parameter(a : felt, b : felt):
    return ()
end

@external
func setup_integers_inverted_range():
    %{ given(a = strategy.integers(200, 100)) %}
    return ()
end

@external
func test_integers_inverted_range(a : felt):
    return ()
end

@external
func setup_multiple_given_calls():
    %{ given(a = strategy.felts()) %}
    %{ given(b = strategy.felts()) %}
    return ()
end

@external
func test_multiple_given_calls(a, b):
    return ()
end
