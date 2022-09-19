%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func __setup__() {
    %{ print("P __setup__") %}
    return ();
}

@external
func setup_should_pass() {
    %{ print("P setup_should_pass") %}
    return ();
}

@external
func test_should_pass{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    %{ print("Hello world!") %}

    assert 0 = 0;
    return ();
}
