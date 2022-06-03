%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

func inverse(x) -> (res):
    with_attr error_message("x must not be zero. Got x={x}."):
        return (res=1 / x)
    end
end

func assert_not_equal(a, b):
    let diff = a - b
    with_attr error_message("a and b must be distinct."):
        inverse(diff)
    end
    return ()
end

# --------------------------------------------------
@view
func test_error_message():
    %{ expect_revert(error_message="a and b must be distinct.") %}
    assert_not_equal(0, 0)
    return ()
end

@view
func test_partial_error_message():
    %{ expect_revert(error_message="must be distinct") %}
    assert_not_equal(0, 0)
    return ()
end

@view
func test_fail_error_message():
    %{ expect_revert(error_message="a and b must be distinct. FOO") %}
    assert_not_equal(0, 0)
    return ()
end

@external
func test_with_except_revert_fail_expected{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_revert("TRANSACTION_FAILED") %}
    assert 0 = 0
    return ()
end

@external
func test_with_except_revert{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_revert("TRANSACTION_FAILED") %}
    assert 0 = 1
    return ()
end

@external
func test_with_except_out_of_scope_revert_fail_expected{syscall_ptr : felt*, range_check_ptr}():
    %{ stop_expecting_revert = expect_revert() %}
    %{ stop_expecting_revert() %}
    assert 0 = 1
    return ()
end

@external
func test_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ expect_revert() %}
    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

@external
func test_call_not_existing_contract_err_message{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ expect_revert("UNINITIALIZED_CONTRACT") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

@external
func test_call_not_existing_contract_fail_expected{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}

    %{ expect_revert("RANDOM_ERROR_NAME") %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

@external
func test_error_was_not_raised_before_stopping_expect_revert_fail_expected{
        syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    local contract_a_address = 42
    %{ stop_expecting_revert() %}

    return ()
end
