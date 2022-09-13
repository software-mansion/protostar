%lang starknet

from starkware.cairo.common.math import assert_in_range

@external
func __setup__() {
    %{ max_examples(3) %}
    return ();
}

@external
func setup_chaining() {
    %{
        given(
            a=strategy.integers(0, 100)
                .filter(lambda x: 17 < x < 100)
                .map(lambda x: x * 2)
                .filter(lambda x: 50 < x < 200)
        )
    %}
    return ();
}

@external
func test_chaining{range_check_ptr}(a) {
    assert_in_range(a, 50, 200);
    return ();
}

@external
func setup_filtering() {
    %{ given(a=strategy.integers(0, 1100).filter(lambda x: 100 <= x <= 1000)) %}
    return ();
}

@external
func test_filtering{range_check_ptr}(a) {
    assert_in_range(a, 100, 1000);
    return ();
}

@external
func setup_mapping() {
    %{ given(a=strategy.integers().map(lambda x: 3)) %}
    return ();
}

@external
func test_mapping(a) {
    assert a = 3;
    return ();
}
