%lang starknet
from src.main import balance, increase_balance
from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func test_increasing_balance{syscall_ptr : felt*, range_check_ptr, pedersen_ptr : HashBuiltin*}():
    let (result_before) = balance.read()
    assert result_before = 0

    increase_balance(42)

    let (result_after) = balance.read()
    assert result_after = 42
    return ()
end

@view
func test_revert_when_negative_value_is_provided{
    syscall_ptr : felt*, range_check_ptr, pedersen_ptr : HashBuiltin*
}():
    let (result_before) = balance.read()
    assert result_before = 0

    %{ expect_revert("TRANSACTION_FAILED") %}
    increase_balance(-42)

    return ()
end
