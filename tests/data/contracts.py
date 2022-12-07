IDENTITY_CONTRACT = """\
%lang starknet

@view
func identity(arg) -> (res: felt) {
    return (arg,);
}
"""

CONTRACT_WITH_CONSTRUCTOR = """\
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt) {
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
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

"""

CONTRACT_WITH_UINT256_CONSTRUCTOR = """\
%lang starknet
from starkware.cairo.common.math import assert_nn
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.uint256 import Uint256, uint256_add

@storage_var
func balance() -> (res: Uint256) {
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: Uint256
) {
    let (res) = balance.read();
    let sum: Uint256 = uint256_add(res, amount);
    balance.write(sum);
    return ();
}

@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: Uint256) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: Uint256
) {
    balance.write(amount);
    return ();
}

"""

FORMATTED_CONTRACT = """\
%lang starknet

@view
func identity(arg) -> felt {
    return arg;
}
"""

UNFORMATTED_CONTRACT = """\
%lang starknet

@view
func identity(arg


) -> felt {
    return arg;
}
"""

BROKEN_CONTRACT = "I LOVE CAIRO"


RUNTIME_ERROR_CONTRACT = """\
%lang starknet

@external
func fail() {
    assert 0 = 1;
    return ();
}
"""
