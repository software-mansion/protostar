%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256
from starkware.cairo.common.alloc import alloc
from starkware.starknet.common.syscalls import deploy

@contract_interface
namespace Proxy:
    func assert_mocked(mocked_target : felt) -> ():
    end
end

@contract_interface
namespace Mocked:
    func get_number() -> (val : felt):
    end
end

@external
func __setup__():
    %{ context.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address %}

    return ()
end

@external
func test_remote_mock{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local to_mock_address : felt
    local proxy_address : felt

    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        ids.proxy_address = deploy_contract("./tests/integration/cheatcodes/mock_call/proxy.cairo").contract_address
        stop_mock = mock_call(ids.to_mock_address, "get_number", [42])
    %}
    Proxy.assert_mocked(proxy_address, to_mock_address)

    %{
        stop_mock()
        expect_revert("TRANSACTION_FAILED", "Not mocked")
    %}

    Proxy.assert_mocked(proxy_address, to_mock_address)
    return ()
end

@external
func test_local_mock{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local to_mock_address : felt
    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        stop_mock = mock_call(ids.to_mock_address, "get_number", [42])
    %}
    let (res1) = Mocked.get_number(to_mock_address)
    assert res1 = 42
    %{ stop_mock() %}
    let (res2) = Mocked.get_number(to_mock_address)
    assert res2 = 1
    return ()
end

@external
func test_missing_remote_mock{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local to_mock_address : felt
    local proxy_address : felt

    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        ids.proxy_address = deploy_contract("./tests/integration/cheatcodes/mock_call/proxy.cairo").contract_address
        expect_revert("TRANSACTION_FAILED", "Not mocked")
    %}

    Proxy.assert_mocked(proxy_address, to_mock_address)
    return ()
end

@external
func test_missing_local_mock{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local to_mock_address : felt
    %{ ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address %}
    let (res2) = Mocked.get_number(to_mock_address)
    assert res2 = 1
    return ()
end

@external
func test_syscall_counter_updated{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local to_mock_address : felt
    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        stop_mock = mock_call(ids.to_mock_address, "get_number", [42])
    %}
    let (res1) = Mocked.get_number(to_mock_address)
    %{ stop_mock() %}
    let (caller) = get_caller_address()
    return ()
end

@external
func test_mock_call_wrong_target{syscall_ptr : felt*, range_check_ptr}():
    %{ stop_mock = mock_call(111, "get_number", [42]) %}
    return ()
end

@external
func test_mock_call_wrong_selector_target{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local to_mock_address : felt
    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        stop_mock = mock_call(111, "get_number_t", [42])
    %}
    return ()
end

@external
func test_mock_call_twice{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local to_mock_address : felt
    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        stop_mock = mock_call(ids.to_mock_address, "get_number", [42])
        stop_mock_2 = mock_call(ids.to_mock_address, "get_number", [666])
    %}

    return ()
end

@external
func test_data_transformation{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local to_mock_address : felt
    %{
        ids.to_mock_address = deploy_contract("./tests/integration/cheatcodes/mock_call/mocked.cairo").contract_address
        mock_call(ids.to_mock_address, "get_number", { "val": 42 })
    %}
    let (val) = Mocked.get_number(to_mock_address)
    assert val = 42
    return ()
end

@external
func test_data_transformation_in_contract_from_setup{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local to_mock_address : felt
    %{
        ids.to_mock_address = context.to_mock_address
        mock_call(ids.to_mock_address, "get_number", { "val": 42 })
    %}
    let (val) = Mocked.get_number(to_mock_address)
    assert val = 42
    return ()
end

@external
func test_data_transformation_with_syscall_deploy{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local class_hash : felt
    %{ ids.class_hash = declare("./tests/integration/cheatcodes/mock_call/mocked.cairo").class_hash %}

    let (local calldata : felt*) = alloc()
    let (contract_address) = deploy(class_hash, 42, 0, calldata, 0)

    %{ mock_call(ids.contract_address, "get_number", { "val": 42 }) %}
    let (val) = Mocked.get_number(contract_address)
    assert val = 42

    return ()
end

@contract_interface
namespace BalanceContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_library_call_not_affected_by_mock{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local balance_class_hash : felt
    local proxy_address : felt
    %{
        ids.balance_class_hash = declare("./tests/integration/cheatcodes/mock_call/balance_contract.cairo").class_hash
        ids.proxy_address = deploy_contract("./tests/integration/cheatcodes/mock_call/delegate_proxy.cairo" , [ids.balance_class_hash]).contract_address
    %}
    BalanceContract.increase_balance(proxy_address, 5)
    let (res) = BalanceContract.get_balance(proxy_address)
    assert res = 5
    return ()
end
