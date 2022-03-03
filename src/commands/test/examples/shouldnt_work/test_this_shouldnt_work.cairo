%lang starknet
from basic import BasicContract

@view
func test_this_shouldnt_work{syscall_ptr : felt*, range_check_ptr}(addr: felt):
    BasicContract.increase_balance(addr, 3)
    let (balance) = BasicContract.get_balance(addr)
    assert balance = 3

    return ()
end