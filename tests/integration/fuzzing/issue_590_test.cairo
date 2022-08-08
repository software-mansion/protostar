%lang starknet

from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

@external
func test_safe_cast_fuzz{range_check_ptr, bitwise_ptr : BitwiseBuiltin*}(val : felt):
    %{
        if (ids.val % 2 == 0 and ids.val > (2**125 - 1) * 2):
            expect_revert()
    %}

    return ()
end
