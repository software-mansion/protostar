%lang starknet
from basic_broken import dummy

@external
func test_broken_contract{syscall_ptr : felt*, range_check_ptr}(contract_address: felt):
    return ()
end
