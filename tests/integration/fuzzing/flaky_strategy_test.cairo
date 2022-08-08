%lang starknet

@external
func test_flaky_strategies{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{
        # We use secrets instead of random, because random is seeded by fuzzer on each run.
        import secrets
        given(a = strategy.integers(0, secrets.randbelow(100)))
    %}
    return ()
end
