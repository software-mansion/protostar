%lang starknet

from broken.basic_broken import constructor, dummy

@external
func test_broken_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address
    %{ id.contract_address = deploy_contract("src/commands/test/examples/broken/basic_broken.cairo") %}
    return ()
end
