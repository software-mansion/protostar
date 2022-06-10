%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@view
func assert_pranked{syscall_ptr : felt*}(expected_caller : felt):
    let (caller_addr) = get_caller_address()
    with_attr error_message("Not pranked"):
        assert caller_addr = expected_caller
    end
    return ()
end
