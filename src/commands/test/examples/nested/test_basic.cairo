%lang starknet

# Check if importing from root directory is possible

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
        ids.contract_a_address = deploy_contract("./src/commands/test/examples/basic.cairo") 
    %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=15)
    return ()
end
