%lang starknet

@external
func __setup__():
    %{ max_examples(5) %}
    return ()
end

@external
func test_max_examples{syscall_ptr : felt*, range_check_ptr}(a, b : felt):
    assert a + b = b + a
    return ()
end
