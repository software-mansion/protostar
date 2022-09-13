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
