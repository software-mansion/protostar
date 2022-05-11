%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@view
func is_pranked{syscall_ptr : felt*}():
    let (caller_addr) = get_caller_address()
    # assert caller_addr = 123

    let (caller_addr) = get_caller_address()
    assert caller_addr = 123
    # assert_not_equal(caller_addr, 123)

    return ()
end
