%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

# @external
# func test_failure_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
#     alloc_locals

# local contract_a_address : felt
#     %{ ids.contract_a_address = 3421347281347298134789213489213 %}

# BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
#     return ()
# end

@external
func test_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

# TEST: error not being thrown while using the callback

# TEST: two expects before calling the callback

# TEST: callback called twice

# TEST: error type full name

# TEST: error type regex

# TEST: error message regex
