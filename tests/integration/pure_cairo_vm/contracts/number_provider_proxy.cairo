%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number,
    get_block_timestamp,
    get_caller_address,
)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace Mocked {
    func get_number() -> (val: felt) {
    }
}

@view
func get_number{syscall_ptr: felt*, range_check_ptr}(mocked_target: felt) -> (val: felt) {
    let (result) = Mocked.get_number(mocked_target);
    return (result,);
}
