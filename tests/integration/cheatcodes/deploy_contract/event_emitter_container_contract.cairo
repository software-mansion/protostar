%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace EventEmitterContract {
    func increase_balance() {
    }
}


@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(address: felt) {
    EventEmitterContract.increase_balance(address);
    return ();
}

