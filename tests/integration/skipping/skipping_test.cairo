%lang starknet

@external
func test_skip() {
    %{ skip(True, "AAA") %}
    return ();
}

@external
func test_skip_false() {
    %{ skip(False, "BBB") %}
    return ();
}

@external
func test_skip_no_reason() {
    %{ skip(True) %}
    return ();
}

@external
func test_skip_no_input() {
    %{ skip() %}
    return ();
}

@external
func test_skip_failed() {
    %{ skip(True, "CCC") %}
    assert 0 = 1;
    return ();
}

@external
func test_skip_false_failed() {
    %{ skip(False, "DDD") %}
    assert 0 = 1;
    return ();
}
