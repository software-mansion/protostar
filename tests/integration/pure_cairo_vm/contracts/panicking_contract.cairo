%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func panic{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    with_attr error_message("PANIC_DESCRIPTION") {
        assert 0 = 1;
    }
    return ();
}
