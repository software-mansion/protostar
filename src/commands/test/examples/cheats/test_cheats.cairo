%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write

@view
func test_roll_cheat{syscall_ptr : felt*}():
    roll(123)
    let (bn) = get_block_number()
    assert bn = 123
    return ()
end

@view
func test_warp_cheat{syscall_ptr : felt*}():
    warp(321)
    let (bt) = get_block_timestamp()
    assert bt = 321
    return ()
end

@view
func test_start_stop_prank_cheat{syscall_ptr : felt*}():
    start_prank(123)
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
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func test_example{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ ids.contract_a_address = deploy_contract("./src/commands/test/examples/basic.cairo") %}

    BasicContract.increase_balance(contract_address=contract_a_address, amount=3)
    let (res) = BasicContract.get_balance(contract_address=contract_a_address)
    assert res = 3
    return ()
end
