%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func add_3{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(a: felt) -> (res: felt) {
    let b = a + 3;
    return (res=b);
}

@view
func error_call{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (res: felt) {
    assert 1=0;
    return (res=1);
}

@view
func add_multiple_values{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(a: felt, b: felt, c: felt) -> (res: felt) {
    let x = a + b + c;
    return (res=x);
}
