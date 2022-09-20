// Declare this file as a StarkNet contract and set the required
// builtins.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.uint256 import Uint256, uint256_add

// Define a storage variable.
@storage_var
func balance() -> (res: Uint256) {
}

@storage_var
func id() -> (res: felt) {
}

// Increases the balance by the given amount.
@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: Uint256
) {
    let (read_balance) = balance.read();
    let (new_balance, carry) = uint256_add(read_balance, amount);
    assert carry = 0;
    balance.write(new_balance);
    return ();
}

// Returns the current balance.
@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    res: Uint256
) {
    let (res) = balance.read();
    return (res,);
}

@view
func get_id{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = id.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    initial_balance: Uint256, contract_id: felt
) {
    balance.write(initial_balance);
    id.write(contract_id);
    return ();
}
