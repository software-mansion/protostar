%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.starknet.common.syscalls import deploy
from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func deployed_contract_address() -> (res: felt) {
}

@external
func deploy_contract{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(class_hash: felt){
    let calldata = alloc();
    let res = deploy(class_hash, 0, 0, calldata.ptr, 0);
    deployed_contract_address.write(res.contract_address);
    return ();
}

@view
func get_deployed_contract_address{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let deployed_ctr_address = deployed_contract_address.read();
    return deployed_ctr_address;
}


