%lang starknet

@view
func __setup__():
    %{ context.foo = {} %}
    return ()
end

@view
func test_should_not_be_executed():
    return ()
end
