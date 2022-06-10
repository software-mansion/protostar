%lang starknet

# Check if importing from root directory is possible

@contract_interface
namespace ProxyContract:
    func set_target(new_target : felt):
    end

    func increase_twice(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

# test deploy basic
# test deploy pranked
# test with constructor args

@external
func test_deploy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address : felt
    %{
        ids.contract_address = Contract("./tests/integration/cheatcodes/deploy_contract_new/basic_contract.cairo").deploy().contract_address 
    %}
    
    BasicContract.increase_balance(contract_address, 5)
    let (res) = BasicContract.get_balance(contract_address)
    assert res = 5
    return ()
end

@external
func test_deploy_contract_pranked{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address : felt
    %{
        prepared_contract = Contract("./tests/integration/cheatcodes/deploy_contract_new/basic_contract.cairo").deploy()
        start_prank(111, target=prepared_contract.contract_address)
        prepared_contract.deploy()
    %}
    
    BasicContract.increase_balance(contract_address, 5)
    let (res) = BasicContract.get_balance(contract_address)
    assert res = 5
    return ()
end


@external
func test_missing_logic_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_logic_address : felt
    local contract_proxy_address : felt
    %{
        ids.contract_proxy_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/proxy_contract.cairo").contract_address
        ids.contract_logic_address = 5342435325345
    %}

    %{ expect_revert() %}

    ProxyContract.set_target(
        contract_address=contract_proxy_address, new_target=contract_logic_address)

    ProxyContract.increase_twice(contract_address=contract_proxy_address, amount=5)
    return ()
end
