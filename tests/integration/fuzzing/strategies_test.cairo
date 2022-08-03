%lang starknet

from starkware.cairo.common.math import assert_le

@external
func test_integers{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{
        given(
            a = st.integers(10, 20),
            b = st.integers(30, 40),
        )
    %}
    assert_le(a, b)
    return ()
end

@external
func test_flaky_strategies{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{
        # We use secrets instead of random, because random is seeded by fuzzer on each run.
        import secrets
        given(a = st.integers(0, secrets.randbelow(100)))
    %}
    return ()
end

@external
func test_unknown_parameter{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{
        given(
            a = st.signed(),
            b = st.integers(min_value=100, max_value=200),
        )
    %}
    return ()
end

@external
func test_not_strategy_object{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{
        given(a = [])
    %}
    return ()
end
