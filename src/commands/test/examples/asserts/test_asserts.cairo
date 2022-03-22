%lang starknet

from asserts import assert_eq, assert_lt, assert_le, assert_gt, assert_ge

@view
func test_assert_eq(contract_address : felt):
    assert_eq(42, 42)

    %{ expect_revert() %}
    assert_eq(21, 37)

    return ()
end

@view
func test_assert_lt(contract_address : felt):
    assert_lt(21, 37)

    %{ expect_revert() %}
    assert_lt(37, 21)

    %{ expect_revert() %}
    assert_lt(42, 42)

    return ()
end

@view
func test_assert_le(contract_address : felt):
    assert_le(21, 37)
    assert_le(42, 42)

    %{ expect_revert() %}
    assert_le(37, 21)

    return ()
end

@view
func test_assert_ge(contract_address : felt):
    assert_ge(37, 21)
    assert_ge(42, 42)

    %{ expect_revert() %}
    assert_ge(21, 37)

    return ()
end

@view
func test_assert_gt(contract_address : felt):
    assert_ge(37, 21)
    assert_ge(42, 42)

    %{ expect_revert() %}
    assert_ge(21, 37)

    return ()
end
