%lang starknet

@external
func test_flaky_strategy{syscall_ptr : felt*, range_check_ptr}(a : felt):
    %{
        # We use secrets instead of random, because random is seeded by fuzzer on each run.
        #
        # The upper bound of random numbers range must be much higher than max_examples
        # fuzz config parameter, in order to minimize the chance of picking the same number
        # twice in sequence.
        import secrets
        given(a = strategy.integers(0, secrets.randbelow(10**9)))
    %}
    return ()
end
