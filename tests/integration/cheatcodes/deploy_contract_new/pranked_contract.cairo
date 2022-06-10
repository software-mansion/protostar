%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@constructor
func constructor{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        initial_balance : Uint256, contract_id : felt):
    balance.write(initial_balance)
    id.write(contract_id)
    return ()
end