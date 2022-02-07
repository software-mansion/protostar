%lang starknet

# Check if importing from root directory is possible
from basic import BasicContract

@external
func test_nested_collection{syscall_ptr : felt*, range_check_ptr}(contract_address: felt):
    return ()
end
