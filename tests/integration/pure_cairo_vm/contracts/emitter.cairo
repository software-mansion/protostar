%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@event
func EVENT_NAME(value: felt) {
}

@event
func EVENT_NAME_2(value: felt) {
}

@external
func emit{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(value: felt) {
    EVENT_NAME.emit(value);
    return ();
}

@external
func emit_2{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(value: felt) {
    EVENT_NAME_2.emit(value);
    return ();
}
