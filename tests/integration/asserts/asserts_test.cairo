%lang starknet

from protostar.asserts import (
    assert_eq, assert_not_eq, assert_signed_lt, assert_signed_le, assert_signed_gt,
    assert_unsigned_lt, assert_unsigned_le, assert_unsigned_gt, assert_signed_ge,
    assert_unsigned_ge)

# ---------------------------------- EQUAL ---------------------------------
@external
func test_assert_eq():
    assert_eq(42, 42)

    %{ expect_revert() %}
    assert_eq(21, 37)

    return ()
end

@external
func test_assert_not_eq():
    assert_not_eq(21, 37)

    %{ expect_revert() %}
    assert_not_eq(42, 42)

    return ()
end

# ---------------------------------- LESS ----------------------------------
@external
func test_assert_signed_lt():
    assert_signed_lt(-21, 37)

    %{ expect_revert() %}
    assert_signed_lt(37, -21)

    %{ expect_revert() %}
    assert_signed_lt(42, 42)

    return ()
end

@external
func test_assert_unsigned_lt():
    assert_unsigned_lt(37, -21)
    assert_unsigned_lt(21, 37)

    %{ expect_revert() %}
    assert_unsigned_lt(37, 21)

    %{ expect_revert() %}
    assert_unsigned_lt(42, 42)

    return ()
end

@external
func test_assert_signed_le():
    assert_signed_le(-21, 37)

    %{ expect_revert() %}
    assert_signed_le(37, -21)

    %{ expect_revert() %}
    assert_signed_le(42, 42)

    return ()
end

@external
func test_assert_unsigned_le():
    assert_unsigned_le(21, 37)
    assert_unsigned_le(42, 42)

    %{ expect_revert() %}
    assert_unsigned_le(37, 21)

    return ()
end

# --------------------------------- GREATER --------------------------------

@external
func test_assert_signed_gt():
    assert_signed_gt(37, -21)
    assert_signed_gt(37, 21)

    %{ expect_revert() %}
    assert_signed_gt(-21, 37)

    %{ expect_revert() %}
    assert_signed_gt(42, 42)

    return ()
end

@external
func test_assert_unsigned_gt():
    assert_unsigned_gt(37, 21)
    assert_unsigned_gt(-21, 37)

    %{ expect_revert() %}
    assert_unsigned_gt(42, 42)

    %{ expect_revert() %}
    assert_unsigned_gt(21, 37)

    return ()
end

@external
func test_assert_signed_ge():
    assert_signed_ge(37, -21)
    assert_signed_ge(37, 21)
    assert_signed_ge(42, 42)

    %{ expect_revert() %}
    assert_signed_ge(-21, 37)

    return ()
end

@external
func test_assert_unsigned_ge():
    assert_unsigned_ge(37, 21)
    assert_unsigned_ge(-21, 37)
    assert_unsigned_ge(42, 42)

    %{ expect_revert() %}
    assert_unsigned_ge(21, 37)

    return ()
end
