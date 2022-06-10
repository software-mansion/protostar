%lang starknet
from starkware.cairo.common.uint256 import Uint256, uint256_add

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
    func increase_balance(amount : Uint256):
    end

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
func test_deploy_contract_with_args_in_constructor{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = deploy_contract("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo", [100, 0, 1]).contract_address %}

    let (res) = BasicWithConstructor.get_balance(contract_address=contract_a_address)
    assert res.low = 100
    assert res.high = 0

    let (id) = BasicWithConstructor.get_id(contract_address=contract_a_address)
    assert id = 1
    return ()
end
