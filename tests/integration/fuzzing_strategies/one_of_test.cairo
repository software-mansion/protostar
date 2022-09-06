%lang starknet

from starkware.cairo.common.math import assert_lt

@external
func __setup__():
    %{ max_examples(3) %}
    return ()
end

@external
func setup_one_of():
    %{
        one_of_strategy = strategy.one_of(strategy.integers(0, 25), strategy.integers(75, 100))

        from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt
        assert type(one_of_strategy.build_strategy(TypeFelt())).__name__ == "OneOfStrategy"

        given(
            a=one_of_strategy,
        )
    %}
    return ()
end

@external
func test_one_of(a, b):
    return ()
end
