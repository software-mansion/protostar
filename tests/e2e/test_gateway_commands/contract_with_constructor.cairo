%lang starknet
from starkware.cairo.common.math import assert_nn
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt) {
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    with_attr error_message("Amount must be positive. Got: {amount}.") {
        assert_nn(amount);
    }

    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    initial_balance: felt
) {
    balance.write(initial_balance);
    return ();
}
