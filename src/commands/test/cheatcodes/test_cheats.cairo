%lang starknet

from cheats import roll, warp, start_prank, stop_prank, mock_call
from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write

@view
func test_roll_cheat{syscall_ptr : felt*}(contract_address : felt):
    roll(123)
    let (bn) = get_block_number()
    assert bn = 123
    return ()
end

@view
func test_warp_cheat{syscall_ptr : felt*}(contract_address : felt):
    warp(321)
    let (bt) = get_block_timestamp()
    assert bt = 321
    return ()
end

@view
func test_start_stop_prank_cheat{syscall_ptr : felt*}(contract_address : felt):
    start_prank(123)
    let (caller_addr) = get_caller_address()
    assert caller_addr = 123

    stop_prank()
    let (caller_addr) = get_caller_address()
    assert_not_equal(caller_addr, 123)

    return ()
end

@view
func test_mock_call{syscall_ptr : felt*, range_check_ptr}(contract_address : felt):
    mock_call(
        0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b,
        1636223440827086009537493065587328807418413867743950350615962740049133672085,
        42)
    let (res) = IBalanceContract.get_balance(
        contract_address=0x3fe90a1958bb8468fb1b62970747d8a00c435ef96cda708ae8de3d07f1bb56b)

    assert res = 42
    return ()
end

@contract_interface
namespace IBalanceContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end
