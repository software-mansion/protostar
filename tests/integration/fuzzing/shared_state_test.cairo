%lang starknet

@external
func test_context(a):
    %{
        context.setup_var = ids.a
        assert context.setup_var == ids.a
    %}
    return ()
end
