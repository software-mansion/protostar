%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func __setup__() {
    %{ print("F __setup__") %}
    return ();
}

@external
func setup_should_fail() {
    %{ print("F setup_should_fail") %}
    return ();
}

@external
func test_should_fail{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    %{
        print(
            "According to all known laws of aviation,\n"
            "there is no way a bee should be able to fly.\n"
            "Its wings are too small to get\n"
            "its fat little body off the ground.\n"
            "The bee, of course, flies anyway\n"
            "because bees don't care\n"
            "what humans think is impossible.\n"
        )
    %}

    assert 1 = 0;
    return ();
}
