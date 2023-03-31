%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt252) {
}

@external
func increase_balance{syscall_ptr: felt252*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt252
) {
    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

@view
func get_balance{syscall_ptr: felt252*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt252) {
    let (res) = balance.read();
    return (res,);
}
