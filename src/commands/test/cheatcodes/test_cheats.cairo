%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write

@view
func test_roll_cheat{syscall_ptr : felt*}(contract_address : felt):
    %{ roll(123) %}
    let (bn) = get_block_number()
    assert bn = 123
    return ()
end

@view
func test_warp_cheat{syscall_ptr : felt*}(contract_address : felt):
    %{ warp(321) %}
    let (bt) = get_block_timestamp()
    assert bt = 321
    return ()
end

@view
func test_start_stop_prank_cheat{syscall_ptr : felt*}(contract_address : felt):
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
func test_mock_call_returning_felt{syscall_ptr : felt*, range_check_ptr}(contract_address : felt):
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_felt", [42]) %}

    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)

    assert res = 42
    return ()
end

@view
func test_mock_call_returning_array{syscall_ptr : felt*, range_check_ptr}(contract_address : felt):
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_array", [1, 42]) %}

    let (res_len, res_arr) = ITestContract.get_array(EXTERNAL_CONTRACT_ADDRESS)

    assert res_arr[0] = 42
    return ()
end

@view
func test_mock_call_returning_struct{syscall_ptr : felt*, range_check_ptr}(contract_address : felt):
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_struct", [21,37]) %}

    let (res_struct) = ITestContract.get_struct(EXTERNAL_CONTRACT_ADDRESS)

    assert res_struct.x = 21
    assert res_struct.y = 37
    return ()
end

@view
func test_clearing_mocks{syscall_ptr : felt*, range_check_ptr}(contract_address : felt):
    tempvar external_contract_address = EXTERNAL_CONTRACT_ADDRESS
    %{ mock_call(ids.external_contract_address, "get_felt", [42]) %}
    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)
    assert res = 42

    %{
        clear_mock_call(ids.external_contract_address, "get_felt")
        except_revert()
    %}

    let (res) = ITestContract.get_felt(EXTERNAL_CONTRACT_ADDRESS)
    return ()
end
