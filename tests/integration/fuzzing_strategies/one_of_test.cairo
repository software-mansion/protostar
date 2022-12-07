%lang starknet

from starkware.cairo.common.math import assert_lt, assert_in_range

@external
func __setup__() {
    %{ max_examples(3) %}
    return ();
}

@external
func setup_one_of() {
    %{
        one_of_strategy = strategy.one_of(strategy.integers(0, 25), strategy.integers(75, 100))

        from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt
        assert type(one_of_strategy.build_strategy(TypeFelt())).__name__ == "OneOfStrategy"

        given(
            a=one_of_strategy,
        )
    %}
    return ();
}

@external
func test_one_of(a) {
    return ();
}

@external
func setup_one_of_filtering() {
    %{
        one_of_strategy = strategy.one_of(
                strategy.integers(0, 25), strategy.integers(75, 100)
            ).filter(
                lambda x: x > 25
            )

        given(
            a=one_of_strategy,
        )
    %}
    return ();
}

@external
func test_one_of_filtering{range_check_ptr}(a) {
    assert_in_range(a, 75, 101);
    return ();
}

@external
func setup_one_of_mapping_and_filtering() {
    %{
        one_of_strategy = strategy.one_of(
                strategy.integers(0, 25), strategy.integers(75, 100)
            ).filter(
                lambda x: x < 25
            ).map(
                lambda x: x + 1
            )

        given(
            a=one_of_strategy,
        )
    %}
    return ();
}

@external
func test_one_of_mapping_and_filtering{range_check_ptr}(a) {
    assert_in_range(a, 1, 26);
    return ();
}
