%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@event
func fake_event() {
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
) {
    fake_event.emit();
    return ();
}
