%lang starknet
%builtins pedersen range_check


@contract_interface
namespace IBasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_balance_increase{syscall_ptr : felt*, range_check_ptr}(contract_address: felt):
    let (beginning_balance) = IBasicContract.get_balance(contract_address)
    assert beginning_balance = 0
    let amt = 10
    IBasicContract.increase_balance(contract_address, amt)
    let (new_balance) = IBasicContract.get_balance(contract_address)
    assert new_balance = 10
    return ()
end
