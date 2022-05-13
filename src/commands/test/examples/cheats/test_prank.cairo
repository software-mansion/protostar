%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace Pranked:
    func assert_pranked() -> ():
    end
end

@external
func test_remote_prank{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address : felt
    %{ 
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/pranked.cairo").contract_address 
        stop_prank = start_prank(123, target_contract_address=ids.contract_address)
    %}
    Pranked.assert_pranked(contract_address=contract_address)

    %{ 
        stop_prank()
        expect_revert("TRANSACTION_FAILED", "Not pranked")
    %}
    
    Pranked.assert_pranked(contract_address=contract_address)
    return ()
end

@external
func test_local_prank{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    %{ stop_prank = start_prank(345) %}
    let (caller_addr) = get_caller_address()
    assert caller_addr = 345

    %{ stop_prank() %}    
    let (caller_addr) = get_caller_address()
    assert_not_equal(caller_addr, 345)
    return ()
end


@external
func test_pranks_only_target{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    local contract_b_address : felt
    %{ 
        ids.contract_a_address = deploy_contract("./src/commands/test/examples/cheats/pranked.cairo").contract_address 
        ids.contract_b_address = deploy_contract("./src/commands/test/examples/cheats/pranked.cairo").contract_address 
        stop_prank = start_prank(123, target_contract_address=ids.contract_a_address)
    %}

    Pranked.assert_pranked(contract_address=contract_a_address)
    
    %{ expect_revert("TRANSACTION_FAILED", "Not pranked") %}
    Pranked.assert_pranked(contract_address=contract_b_address)
    return ()
end

@external
func test_syscall_counter_correct{syscall_ptr : felt*, range_check_ptr}():
    %{ 
        stop_prank = start_prank(345)
    %}
    let (caller_addr) = get_caller_address()
    assert caller_addr = 345
    # We check if syscall counter has been correctly incremented
    # It will throw an error if it hasn't been incremented
    let (bn) = get_block_number()
    return ()
end

@external
func test__missing_remote_prank{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address : felt
    %{ 
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/pranked.cairo").contract_address
        expect_revert("TRANSACTION_FAILED", "Not pranked")
    %}
    Pranked.assert_pranked(contract_address=contract_address)
    return ()
end

@external
func test_missing_local_prank{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    %{ 
        expect_revert("TRANSACTION_FAILED")
    %}
    let (caller_addr) = get_caller_address()
    assert caller_addr = 123
    return ()
end

@external
func test_prank_wrong_target{syscall_ptr : felt*, range_check_ptr}():
    %{ 
        stop_prank = start_prank(123, target_contract_address=123)
    %}
    return ()
end
