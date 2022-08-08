%lang starknet

from starkware.cairo.common.math import assert_le
from starkware.cairo.common.math_cmp import is_nn

# This test checks that the `integers` strategy can have one of it's parameters omitted.
# Because the range will be unlimited at least in one end, the fuzzer is expected to find
# values that will overflow. Here, we try to ensure that nothing crashes along the way.
#
# We split the real integers range into two halves (with pivot point in the middle),
# and compare samples from both spaces that values from lower half are less than or equal to
# values from higher half, if the comparison is possible within Cairo range check semantics.
#
# Usage of `PRIME // 2` as the pivot point helps the fuzzer find felt overflowing values.
@external
func test_integers_unbounded{syscall_ptr : felt*, range_check_ptr}(a : felt, b : felt):
    alloc_locals
    %{
        pivot = PRIME // 2
        given(
            a = strategy.integers(max_value=pivot),
            b = strategy.integers(min_value=pivot),
        )
    %}
    let (local is_a_nn) = is_nn(a)
    let (local is_b_nn) = is_nn(b)
    if is_a_nn == 1:
        if is_b_nn == 1:
            assert_le(a, b)
            tempvar range_check_ptr=range_check_ptr
        else:
            tempvar range_check_ptr=range_check_ptr
        end
    else:
        tempvar range_check_ptr=range_check_ptr
    end
    return ()
end
