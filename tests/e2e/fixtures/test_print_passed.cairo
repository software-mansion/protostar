%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func __setup__():
    %{ print("P_SETUP") %}
    return ()
end

@external
func test_should_pass{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():

    %{
        print("Hello world!")
    %}


    assert 0 = 0
    return ()
end