%lang starknet

@external
func setup_zero() {
    %{ max_examples(0) %}
    return ();
}

@external
func test_zero(a) {
    return ();
}

@external
func setup_negative() {
    %{ max_examples(-1) %}
    return ();
}

@external
func test_negative(a) {
    return ();
}
