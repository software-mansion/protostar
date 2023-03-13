use array::ArrayTrait;

#[test]
fn test_ok() {
    assert(1 == 1, 'simple check');
}

#[test]
fn test_panic_single_value() {
    let mut data = array_new::<felt>();
    array_append::<felt>(ref data, 21);
    panic(data)
}

#[test]
fn test_panic_multiple_values() {
    let mut data = array_new::<felt>();
    array_append::<felt>(ref data, 101);
    array_append::<felt>(ref data, 102);
    array_append::<felt>(ref data, 103);
    panic(data)
}
