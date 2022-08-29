%lang starknet

@external
func setup_zero():
    %{ max_examples(0) %}
    return ()
end

@external
func test_zero(a):
    return ()
end

@external
func setup_negative():
    %{ max_examples(-1) %}
    return ()
end

@external
func test_negative(a):
    return ()
end
