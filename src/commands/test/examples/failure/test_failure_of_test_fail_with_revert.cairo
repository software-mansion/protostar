%lang starknet
%builtins pedersen range_check

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_fail_when_expect_revert_is_used{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_revert() %}
    BasicContract.increase_balance(contract_address=1234, amount=5)
    return ()
end
