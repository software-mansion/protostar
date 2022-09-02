%lang starknet

from starkware.cairo.common.math import assert_le

@external
func setup_integers():
    %{
        max_examples(5)

        given(
            a = strategy.integers(10, 20),
            b = strategy.integers(30, 40),
        )
    %}
    return ()
end

@external
func test_integers{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    assert_le(a, b)
    return ()
end
