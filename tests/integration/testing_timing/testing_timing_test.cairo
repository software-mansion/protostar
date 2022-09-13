%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func test_failed_sleep{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    %{
        from asyncio import sleep
        sleep(1)
    %}

    assert 1 = 0;
    return ();
}

@external
func test_failed_simple{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    assert 1 = 0;
    return ();
}

@external
func test_passed_sleep{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    %{
        from asyncio import sleep
        sleep(0.5)
    %}

    assert 0 = 0;
    return ();
}

@external
func test_passed_simple{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    assert 0 = 0;
    return ();
}
