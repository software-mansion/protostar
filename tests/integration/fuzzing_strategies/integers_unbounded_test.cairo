%lang starknet

# This test checks that the `integers` strategy can have one of it's parameters omitted.
# Because the range will be unlimited at least in one end, the fuzzer is expected to find
# values that will overflow. Here, we try to ensure that nothing crashes along the way,
# and raise an assertion error when the overflow happens, so that the test does not run
# for too long.
#
# We split the real integers range into two halves (with pivot point in the middle),
# and compare samples from both spaces that values from lower half are less than or equal to
# values from higher half, if the comparison is possible within Cairo range check semantics.
#
# Usage of `PRIME // 2` as the pivot point helps the fuzzer find felt overflowing values.

@external
func setup_integers_unbounded():
    %{
        max_examples(60)

        pivot = PRIME // 2
        given(
            a = strategy.integers(max_value=pivot),
            b = strategy.integers(min_value=pivot),
        )
    %}
    return ()
end

@external
func test_integers_unbounded{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    %{ assert ids.a <= ids.b %}
    return ()
end
