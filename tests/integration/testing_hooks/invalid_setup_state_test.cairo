%lang starknet

@view
func setup_state():
    %{ context.foo = {} %}
    return ()
end

@view
func test_should_not_be_executed():
    return ()
end
