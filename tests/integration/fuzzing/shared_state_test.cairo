%lang starknet

@external
func setup_context() {
    %{ given(a = strategy.felts()) %}
    return ();
}

@external
func test_context(a) {
    %{
        context.setup_var = ids.a
        assert context.setup_var == ids.a
    %}
    return ();
}
