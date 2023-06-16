use array::ArrayTrait;

#[test]
fn test_ok() {
    assert(1 == 1, 'simple check');
}

#[test]
fn test_assert_err_code_not_ascii() {
    assert(1 == 2, 1234);
}

#[test]
fn test_panic_single_value() {
    let mut data = ArrayTrait::new();
    data.append(21);
    panic(data)
}

#[test]
fn test_panic_multiple_values() {
    let mut data = ArrayTrait::new();
    data.append('elaborate');
    data.append('panic');
    data.append('data is here');
    panic(data)
}
