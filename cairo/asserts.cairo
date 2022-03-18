from starkware.cairo.common.math import assert_le as _assert_le, split_felt

# This version of split_felt doesn't require range_check_ptr
func _split_felt(value) -> (high, low):
    const MAX_HIGH = (-1) / 2 ** 128
    const MAX_LOW = 0

    tempvar low
    tempvar high
    %{
        from starkware.cairo.common.math_utils import assert_integer
        assert ids.MAX_HIGH < 2**128 and ids.MAX_LOW < 2**128
        assert PRIME - 1 == ids.MAX_HIGH * 2**128 + ids.MAX_LOW
        assert_integer(ids.value)
        ids.low = ids.value & ((1 << 128) - 1)
        ids.high = ids.value >> 128
    %}
    assert value = high * (2 ** 128) + low
    return (high=high, low=low)
end

func assert_signed_eq(a : felt, b : felt):
    assert a = b
    return ()
end

func assert_unsigned_eq(a : felt, b : felt):
    alloc_locals
    let (local a_high, local a_low) = _split_felt(a)
    let (b_high, b_low) = _split_felt(b)

    %{ assert ids.a_low == ids.b_low, f"unsigned value of a = {ids.a_low} is not equal to b = {ids.b_low}" %}
    assert a_low = b_low

    return ()
end
