%lang starknet
from starkware.starknet.common.syscalls import get_contract_address
from starkware.cairo.common.uint256 import Uint256

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
namespace BasicWithConstructor:
    func get_balance() -> (res : Uint256):
    end

    func get_id() -> (res : felt):
    end
end

@external
func test_proxy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_logic_address : felt
    local contract_proxy_address : felt
    %{
        ids.contract_proxy_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/proxy_contract.cairo").contract_address 
        ids.contract_logic_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_contract.cairo").contract_address
    %}

    ProxyContract.set_target(
        contract_address=contract_proxy_address, new_target=contract_logic_address)

    ProxyContract.increase_twice(contract_address=contract_proxy_address, amount=5)

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
        ids.contract_proxy_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/proxy_contract.cairo").contract_address
        ids.contract_logic_address = 5342435325345
    %}

    %{ expect_revert() %}

    ProxyContract.set_target(
        contract_address=contract_proxy_address, new_target=contract_logic_address)

    ProxyContract.increase_twice(contract_address=contract_proxy_address, amount=5)
    return ()
end

@external
func test_passing_constructor_data_as_list{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local deployed_contract_address : felt
    let (contract_address) = get_contract_address()

    %{
        ids.deployed_contract_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo",
            [42, 0, ids.contract_address]
        ).contract_address
    %}

    let (balance) = BasicWithConstructor.get_balance(deployed_contract_address)
    let (id) = BasicWithConstructor.get_id(deployed_contract_address)

    assert balance.low = 42
    assert balance.high = 0
    assert id = contract_address

    return ()
end

@external
func test_data_transformation{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local deployed_contract_address : felt
    let (contract_address) = get_contract_address()

    %{
        ids.deployed_contract_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo",
            { "initial_balance": 42, "contract_id": ids.contract_address }
        ).contract_address
    %}

    let (balance) = BasicWithConstructor.get_balance(deployed_contract_address)
    let (id) = BasicWithConstructor.get_id(deployed_contract_address)

    assert balance.low = 42
    assert balance.high = 0
    assert id = contract_address

    return ()
end
