%lang starknet

@external
func setup_zero() {
    %{ max_examples(0) %}
    %{ given(a = strategy.felts()) %}
    return ();
}

@external
func test_zero(a) {
    return ();
}

@external
func setup_negative() {
    %{ max_examples(-1) %}
    %{ given(a = strategy.felts()) %}
    return ();
}

@external
func test_negative(a) {
    return ();
}
