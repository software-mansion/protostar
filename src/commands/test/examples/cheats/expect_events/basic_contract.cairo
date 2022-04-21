%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

@event
func balance_increased(current_balance : felt, amount : felt):
end

@external
func increase_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    balance_increased.emit(current_balance=37, amount=21)
    return ()
end
