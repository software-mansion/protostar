%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func dummy() {
    return ();
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    assert 1 = 0;
    return ();
}
