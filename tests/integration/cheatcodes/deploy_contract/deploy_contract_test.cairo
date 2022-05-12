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


@external
func test_proxy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_logic_address : felt
    local contract_proxy_address : felt
    %{ 
        ids.contract_proxy_address = deploy_contract("src/commands/test/examples/cheats/complex/proxy_contract.cairo").contract_address 
        ids.contract_logic_address = deploy_contract("./src/commands/test/examples/basic.cairo").contract_address 
    %}

    ProxyContract.set_target(
        contract_address=contract_proxy_address,
        new_target=contract_logic_address
    )

    ProxyContract.increase_twice(
        contract_address=contract_proxy_address,
        amount=5
    )

    let (res) = ProxyContract.get_balance(contract_address=contract_proxy_address)
    assert res = 10
    return ()
end

@external
func test_missing_logic_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_logic_address : felt
    local contract_proxy_address : felt
    %{ 
        ids.contract_proxy_address = deploy_contract("src/commands/test/examples/cheats/complex/proxy_contract.cairo").contract_address
        ids.contract_logic_address = 5342435325345
    %}

    %{ expect_revert() %}

    ProxyContract.set_target(
        contract_address=contract_proxy_address,
        new_target=contract_logic_address
    )

    ProxyContract.increase_twice(
        contract_address=contract_proxy_address,
        amount=5
    )
    return ()
end
