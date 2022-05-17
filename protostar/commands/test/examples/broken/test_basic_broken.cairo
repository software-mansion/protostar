%lang starknet

@external
func test_broken_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local contract_address
    %{ id.contract_address = deploy_contract("protostar/commands/test/examples/broken/basic_broken.cairo").contract_address %}
    return ()
end
