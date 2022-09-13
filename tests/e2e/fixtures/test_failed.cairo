%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func test_should_fail{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    assert 1 = 0;
    return ();
}
