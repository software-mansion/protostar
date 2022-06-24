%lang starknet

@external
func __setup__():
    %{ context.foo = {} %}
    return ()
end

@external
func test_should_not_be_executed():
    return ()
end
