%lang starknet

from asserts import assert_signed_eq, assert_unsigned_eq

@view
func test_assert_eq(contract_address : felt):
    assert_signed_eq(42, 42)
    %{ expect_revert() %}
    assert_signed_eq(21, 37)

    return ()
end

@view
func test_assert_unsigned_eq(contract_address : felt):
    assert_unsigned_eq(-42, 42)
    return ()
end
