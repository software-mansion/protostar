%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func id() -> (id: felt) {
}
@storage_var
func balance() -> (res: felt) {
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    _id: felt, starting_balance: felt
) {
    balance.write(starting_balance);
    id.write(_id);
    return ();
}

@view
func get_id{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = id.read();
    return (res,);
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount_1: felt,
    amount_2: felt,
    amount_3: felt,
) -> () {
    let (res) = balance.read();
    balance.write(res + amount_1 + amount_2 + amount_3);
    return ();
}

@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}
