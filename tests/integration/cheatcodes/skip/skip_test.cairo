%lang starknet

@external
func setup_skip() {
    %{ skip("REASON") %}
    return ();
}

@external
func test_skip() {
    return ();
}

///

@external
func setup_skip_no_reason() {
    %{ skip() %}
    return ();
}

@external
func test_skip_no_reason() {
    return ();
}

///

@external
func test_skip_outside_of_setup() {
    %{ skip("INVALID") %}
    return ();
}
