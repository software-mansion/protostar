%lang starknet

from starkware.starknet.common.syscalls import get_block_timestamp

@view
func test_changing_timestamp{syscall_ptr : felt*}():
    %{ warp(321) %}
    let (bt) = get_block_timestamp()
    assert bt = 321
    return ()
end
