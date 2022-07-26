%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.starknet.common.syscalls import deploy

@external
func test_deploy_declared_contract{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals

    local class_hash : felt
    %{ ids.class_hash = declare("./tests/integration/constructor_in_tested_file/basic_contract.cairo").class_hash %}

    let (local calldata : felt*) = alloc()
    let (contract_address) = deploy(class_hash, 42, 0, calldata, 0)

    return ()
end
