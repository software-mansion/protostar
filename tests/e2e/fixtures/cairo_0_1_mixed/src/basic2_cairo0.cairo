%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance2() -> (res: felt) {
}

@external
func increase_balance2{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    let (res) = balance2.read();
    balance2.write(res + amount);
    return ();
}

@view
func get_balance2{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance2.read();
    return (res,);
}
