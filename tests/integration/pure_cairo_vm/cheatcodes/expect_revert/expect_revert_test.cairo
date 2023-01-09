func inverse(x) -> (res: felt) {
    with_attr error_message("x must not be zero. Got x={x}.") {
        return (res=1 / x);
    }
}

func assert_not_equal(a, b) {
    let diff = a - b;
    with_attr error_message("a and b must be distinct.") {
        inverse(diff);
    }
    return ();
}

func test_error_message() {
    %{ expect_revert(error_message="a and b must be distinct.") %}
    assert_not_equal(0, 0);
    return ();
}

func test_partial_error_message() {
    %{ expect_revert(error_message="must be distinct") %}
    assert_not_equal(0, 0);
    return ();
}

func test_fail_error_message() {
    %{ expect_revert(error_message="a and b must be distinct. FOO") %}
    assert_not_equal(0, 0);
    return ();
}

func test_with_except_revert_fail_expected() {
    %{ expect_revert("TRANSACTION_FAILED") %}
    assert 0 = 0;
    return ();
}

func test_with_except_revert() {
    %{ expect_revert("TRANSACTION_FAILED") %}
    assert 0 = 1;
    return ();
}

func test_with_except_out_of_scope_revert_fail_expected() {
    %{ stop_expecting_revert = expect_revert() %}
    %{ stop_expecting_revert() %}
    assert 0 = 1;
    return ();
}

func test_error_was_not_raised_before_stopping_expect_revert_fail_expected() {
    alloc_locals;

    %{ stop_expecting_revert = expect_revert("UNINITIALIZED_CONTRACT") %}
    local contract_a_address = 42;
    %{ stop_expecting_revert() %}

    return ();
}

func test_already_expecting_error_message_when_no_arguments_were_provided() {
    %{
        expect_revert()
        expect_revert()
    %}

    return ();
}
