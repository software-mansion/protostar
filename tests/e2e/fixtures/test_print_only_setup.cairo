%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func __setup__():
    %{ print("O __setup__") %}
    return ()
end

@external
func test_should_pass{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    assert 0 = 0
    return ()
end
