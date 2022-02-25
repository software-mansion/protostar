%lang starknet

from cheats import roll, warp, start_prank, stop_prank
from starkware.starknet.common.syscalls import (
   get_block_number, get_block_timestamp, get_caller_address
)
from starkware.cairo.common.math import assert_not_equal

@view
func test_roll_cheat{syscall_ptr: felt*}(contract_address: felt):
   roll(123)
   let (bn) = get_block_number()
   assert bn = 123
   return ()
end

@view
func test_warp_cheat{syscall_ptr: felt*}(contract_address: felt):
   warp(321)
   let (bt) = get_block_timestamp()
   assert bt = 321
   return ()
end

@view
func test_start_stop_prank_cheat{syscall_ptr: felt*}(contract_address: felt):
   start_prank(123)
   let (caller_addr) = get_caller_address()
   assert caller_addr = 123


   stop_prank()
   let (caller_addr) = get_caller_address()
   assert_not_equal(caller_addr, 123)

   return ()
end