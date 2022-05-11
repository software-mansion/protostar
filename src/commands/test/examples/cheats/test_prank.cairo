%lang starknet

from starkware.starknet.common.syscalls import (
    get_block_number, get_block_timestamp, get_caller_address)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace Pranked:
    func is_pranked() -> ():
    end
end

@external
func test_deploy_contract_with_args_in_constructor{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_a_address : felt
    %{ 
        ids.contract_a_address = deploy_contract("./src/commands/test/examples/cheats/pranked.cairo").contract_address 
        # start_prank(123, ids.contract_a_address)
        start_prank(123)
    %}
    let (caller_addr) = get_caller_address()
    assert caller_addr = 123
    %{
        stop_prank() 
    %}

    Pranked.is_pranked(contract_address=contract_a_address)
    return ()
end
