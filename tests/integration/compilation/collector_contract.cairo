%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

const CONST_VAL = 12234214

func internal_function{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    assert 0 = 0
    return ()
end

@external
func test_case1{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    internal_function()
    return ()
end

@view
func test_case2{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    internal_function()
    return ()
end

