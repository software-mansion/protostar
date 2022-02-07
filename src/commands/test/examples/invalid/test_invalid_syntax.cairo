%lang starknet
from basic import BasicContract

@invalid_syntax
func test_broken{syscall_ptr : felt*, range_check_ptr}(contract_address: felt):
end
