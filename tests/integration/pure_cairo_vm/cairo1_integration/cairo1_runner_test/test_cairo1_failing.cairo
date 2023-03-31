use array::ArrayTrait;

#[test]
fn test_ok() {
    assert(1 == 1, 'simple check');
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
    data.append(101);
    data.append(102);
    data.append(103);
    panic(data)
}

