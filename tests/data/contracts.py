IDENTITY_CONTRACT = """\
%lang starknet

@view
func identity(arg) -> (res: felt) {
    return (arg,);
}
"""

CONTRACT_WITH_CONSTRUCTOR = """\
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res: felt) {
}

@external
func increase_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    amount: felt
) {
    let (res) = balance.read();
    balance.write(res + amount);
    return ();
}

@view
func get_balance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    let (res) = balance.read();
    return (res,);
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    initial_balance: felt
) {
    balance.write(initial_balance);
    return ();
}

"""

FORMATTED_CONTRACT = """\
%lang starknet

@view
func identity(arg) -> felt {
    return arg;
}
"""

UNFORMATTED_CONTRACT = """\
%lang starknet

@view
func identity(arg


) -> felt {
    return arg;
}
"""

BROKEN_CONTRACT = "I LOVE CAIRO"


RUNTIME_ERROR_CONTRACT = """\
%lang starknet

@external
func fail() {
    assert 0 = 1;
    return ();
}
"""

PROXY_CONTRACT = """\
%lang starknet
%builtins pedersen range_check bitwise

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import library_call

@storage_var
func implementation_hash() -> (class_hash: felt) {
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    implementation_hash_: felt
) {
    implementation_hash.write(value=implementation_hash_);
    return ();
}

@external
@raw_input
@raw_output
func __default__{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    selector: felt, calldata_size: felt, calldata: felt*
) -> (retdata_size: felt, retdata: felt*) {
    let (class_hash) = implementation_hash.read();

    let (retdata_size: felt, retdata: felt*) = library_call(
        class_hash=class_hash,
        function_selector=selector,
        calldata_size=calldata_size,
        calldata=calldata,
    );
    return (retdata_size=retdata_size, retdata=retdata);
}
 
"""
