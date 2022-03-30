%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_example{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ 
        ids.contract_a_address = deploy_contract("./src/main.cairo").contract_address
    %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=15)
    let (res) = BasicContract.get_balance(contract_address=contract_a_address)
    assert res = 15
    return ()
end
