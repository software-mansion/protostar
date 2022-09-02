%lang starknet

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

func helper{}():
    [ap + 2000] = 111
    [ap + 10000] = 222
    ret
end

func helper2{}():
    [ap + 300] = 555
    ret
end

@external
func test_deploy_contract_simplified{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{ 
        basic_contract = deploy_contract("./tests/integration/profile_tests/basic_contract.cairo")
        ids.contract_address = basic_contract.contract_address 
    %}
    helper()
    # helper2()

    BasicContract.increase_balance(contract_address, 5)
    let (res) = BasicContract.get_balance(contract_address)
    assert res = 5
    return ()
end

# @external
# func test_printing_resource_usage_in_integration_testing_approach{
#     syscall_ptr : felt*, range_check_ptr
# }():
#     alloc_locals

#     local z: felt
#     %{
#         basic_contract = deploy_contract("tests/integration/profile_tests/basic_contract.cairo")
#         ids.z = basic_contract.contract_address
#     %}
#     # helper()
#     # helper2()
#     BasicContract.increase_balance(z, 5)
#     return ()
# end

