%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@view
func test_roll_cheat{syscall_ptr : felt*}():
    %{ roll(123) %}
    let (bn) = get_block_number()
    assert bn = 123
    return ()
end

@view
func test_warp_cheat{syscall_ptr : felt*}():
    %{ warp(321) %}
    let (bt) = get_block_timestamp()
    assert bt = 321
    return ()
end

@view
func test_start_stop_prank_cheat{syscall_ptr : felt*}():
    %{ start_prank(123) %}
    let (caller_addr) = get_caller_address()
    assert caller_addr = 123

    %{ stop_prank() %}
    let (caller_addr) = get_caller_address()
    assert_not_equal(caller_addr, 123)

    return ()
end

const EXTERNAL_CONTRACT_ADDRESS = 0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b

struct Point:
    member x : felt
    member y : felt
end

@contract_interface
namespace ITestContract:
    func get_felt() -> (res : felt):
    end

    func get_array() -> (res_len : felt, res : felt*):
    end

    func get_struct() -> (res : Point):
    end
end

@view
func test_mock_call_returning_felt{syscall_ptr : felt*, range_check_ptr}():
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_felt", [42]) %}

    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)

    assert res = 42
    return ()
end

@view
func test_mock_call_returning_array{syscall_ptr : felt*, range_check_ptr}():
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_array", [1, 42]) %}

    let (res_len, res_arr) = ITestContract.get_array(EXTERNAL_CONTRACT_ADDRESS)

    assert res_arr[0] = 42
    return ()
end

@view
func test_mock_call_returning_struct{syscall_ptr : felt*, range_check_ptr}():
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_struct", [21,37]) %}

    let (res_struct) = ITestContract.get_struct(EXTERNAL_CONTRACT_ADDRESS)

    assert res_struct.x = 21
    assert res_struct.y = 37
    return ()
end

@view
func test_clearing_mocks{syscall_ptr : felt*, range_check_ptr}():
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_felt", [42]) %}
    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)
    assert res = 42

    %{
        clear_mock_call(ids.external_contract_address, "get_felt")
        expect_revert()
    %}

    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)
    return ()
end

# deploy_contract
@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_deploy_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = deploy_contract("./protostar/commands/test/examples/basic.cairo").contract_address %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    let (res) = BasicContract.get_balance(contract_address=contract_a_address)
    assert res = 3
    return ()
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
func test_deploy_contract_with_args_in_constructor{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = deploy_contract("./protostar/commands/test/examples/basic_with_constructor.cairo", [100, 0, 1]).contract_address %}

    let (res) = BasicWithConstructor.get_balance(contract_address=contract_a_address)
    assert res.low = 100
    assert res.high = 0

    let (id) = BasicWithConstructor.get_id(contract_address=contract_a_address)
    assert id = 1
    return ()
end

@external
func test_call_not_existing_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}
    %{ expect_revert() %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end

@external
func test_call_not_existing_contract_specific_error{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = 3421347281347298134789213489213 %}
    %{ expect_revert("UNINITIALIZED_CONTRACT") %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    return ()
end
