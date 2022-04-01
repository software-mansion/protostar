%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_fail_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

@external
func test_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

@external
func test_stop_expecting{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    %{ stop_expecting_revert() %}

    return ()
end

@external
func test_fail_error_was_not_raised_before_stopping_expect_revert{
        syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    local contract_a_address = 42
    %{ stop_expecting_revert() %}

    return ()
end

@external
func test_fail_stop_expecting_called_before_error{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    %{ stop_expecting_revert() %}

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    %{ stop_expecting_revert() %}

    return ()
end

# @external
# func test_fail_two_expect_revert_calls{syscall_ptr : felt*, range_check_ptr}():
#     alloc_locals

# local contract_a_address : felt
#     %{ ids.contract_a_address = 3421347281347298134789213489213 %}

# %{
#         expect_revert("UNINITIALIZED_CONTRACT")
#         stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT")
#     %}
#     BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
#     %{ stop_expecting_revert() %}

# return ()
# end

# TEST: callback called twice

# TEST: error type full name

# TEST: error type regex

# TEST: error message regex
