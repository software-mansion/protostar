%lang starknet
from starkware.starknet.common.syscalls import get_block_number

@view
func test_changing_block_number{syscall_ptr : felt*}():
    %{ roll(123) %}
    let (bn) = get_block_number()
    assert bn = 123
    return ()
end
