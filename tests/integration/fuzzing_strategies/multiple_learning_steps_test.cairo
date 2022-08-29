%lang starknet

from starkware.cairo.common.math import assert_le

@external
func __setup__():
    %{ max_examples(5) %}
    return ()
end

@external
func test_multiple_learning_steps{syscall_ptr : felt*, range_check_ptr}(a, b, c, d):
    %{ given(a = strategy.integers(10, 20)) %}
    %{ given(b = strategy.integers(30, 40)) %}
    %{ given(c = strategy.felts()) %}
    assert_le(a, b)
    return ()
end
