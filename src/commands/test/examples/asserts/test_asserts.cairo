from asserts import assert_eq

func test_assert_eq():
    alloc_locals
    local a = 42

    assert_eq(a, 42)

    %{ expect_revert() %}
    assert_eq(a, 24)

    return ()
end
