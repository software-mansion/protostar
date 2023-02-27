%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_number

@storage_var
func stored_block_number() -> (res: felt) {
}

@view
func get_stored_block_number{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_number) = stored_block_number.read();
    return (res=block_number);
}

@view
func get_syscall_block_number{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (block_number) = get_block_number();
    return (res=block_number);
}

@external
func set_stored_block_number_to_syscall_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    let (block_number) = get_block_number();
    stored_block_number.write(block_number);

    return ();
}

@contract_interface
namespace BlockNumberTesterContract {
    func set_stored_block_number_to_syscall_value() {
    }
}

@external
func call_set_stored_block_number_to_syscall_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(contract_address: felt) {
    BlockNumberTesterContract.set_stored_block_number_to_syscall_value(contract_address=contract_address);
    return ();
}
