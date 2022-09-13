// Declare this file as a StarkNet contract and set the required
// builtins.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.alloc import alloc
from starkware.starknet.common.syscalls import deploy

@contract_interface
namespace BasicContract {
    func increase_balance(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

@external
func deploy_contract_from_proxy{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    class_hash_d: felt
) -> (address: felt) {
    alloc_locals;
    let (local calldata: felt*) = alloc();
    let (contract_address) = deploy(class_hash_d, 42, 0, calldata, 0);
    return (contract_address,);
}
