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

func test_outer_error_message() {
    %{ expect_panic("a and b must be distinct.") %}
    assert_not_equal(0, 0);
    return ();
}

func test_inner_error_message() {
    %{ expect_panic("x must not be zero. Got x=0.") %}
    assert_not_equal(0, 0);
    return ();
}

func test_partial_error_message() {
    %{ expect_panic("must be distinct") %}
    assert_not_equal(0, 0);
    return ();
}

func test_fail_error_message() {
    %{ expect_panic("a and b must be distinct. FOO") %}
    assert_not_equal(0, 0);
    return ();
}

func test_fail_when_expected_panic() {
    %{ expect_panic() %}
    assert 0 = 0;
    return ();
}

func test_with_except_revert() {
    %{ expect_panic() %}
    assert 0 = 1;
    return ();
}

func test_with_except_out_of_scope_revert_fail_expected() {
    %{ assert_panic = expect_panic() %}
    %{ assert_panic() %}
    assert 0 = 1;
    return ();
}

func test_error_was_not_raised_before_stopping_expect_revert_fail_expected() {
    alloc_locals;
    %{ assert_panic = expect_panic() %}
    local contract_a_address = 42;
    %{ assert_panic() %}
    return ();
}

func test_already_expecting_error_message_when_no_arguments_were_provided() {
    %{
        expect_panic()
        expect_panic()
    %}
    return ();
}
