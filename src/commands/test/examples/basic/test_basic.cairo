%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_increase_balance{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = deploy_contract("./src/commands/test/examples/basic.cairo").contract_address %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=15)
    return ()
end

@external
func test_cannot_call_methods_of_not_deployed_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    %{ expect_revert() %}

    local contract_a_address : felt
    %{ ids.contract_a_address = 34134124 %}
    BasicContract.increase_balance(contract_address=contract_a_address, amount=15)
    return ()
end
