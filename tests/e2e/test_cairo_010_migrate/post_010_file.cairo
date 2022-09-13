%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func storage_felt() -> (res: felt) {
}

@external
func set_var{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(val: felt) {
    storage_felt.write(val);

    return ();
}

@view
func view_val{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (val_now) = storage_felt.read();
    return (res=val_now);
}
