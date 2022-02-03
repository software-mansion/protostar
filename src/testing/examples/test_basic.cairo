%lang starknet
from basic import BasicContract

@external
func test_balance_increase{syscall_ptr : felt*, range_check_ptr}(contract_address: felt):
    let (beginning_balance) = BasicContract.get_balance(contract_address)
    assert beginning_balance = 0
    let amt = 10
    BasicContract.increase_balance(contract_address, amt)
    let (new_balance) = BasicContract.get_balance(contract_address)
    assert new_balance = 10
    return ()
end
