%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.starknet.common.syscalls import deploy

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@contract_interface
namespace ProxyContract:
    func deploy_contract_from_proxy(class_hash_d : felt) -> (address : felt):
    end
end

@external
func test_deploy_declared_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local class_hash : felt
    %{ ids.class_hash = declare("./tests/integration/cheatcodes/declare/basic_contract.cairo").class_hash %}

    let (local calldata : felt*) = alloc()
    let (contract_address) = deploy(class_hash, 42, 0, calldata, 0)

    BasicContract.increase_balance(contract_address, 12)

    let (balance) = BasicContract.get_balance(contract_address)
    assert balance = 12
    return ()
end

@external
func test_deploy_declared_contract_deploy_zero_flag{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local class_hash : felt
    %{ ids.class_hash = declare("./tests/integration/cheatcodes/declare/basic_contract.cairo").class_hash %}

    let (local calldata : felt*) = alloc()
    let (contract_address) = deploy(class_hash, 42, 0, calldata, 1)

    BasicContract.increase_balance(contract_address, 12)

    let (balance) = BasicContract.get_balance(contract_address)
    assert balance = 12
    return ()
end

@external
func test_deploy_declared_contract_in_proxy{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local proxy_address : felt
    local class_hash : felt
    %{
        ids.proxy_address = deploy_contract("./tests/integration/cheatcodes/declare/proxy_contract.cairo").contract_address
        ids.class_hash = declare("./tests/integration/cheatcodes/declare/basic_contract.cairo").class_hash
    %}

    let (contract_address) = ProxyContract.deploy_contract_from_proxy(proxy_address, class_hash)

    BasicContract.increase_balance(contract_address, 12)

    let (balance) = BasicContract.get_balance(contract_address)
    assert balance = 12
    return ()
end
