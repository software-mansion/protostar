use array::ArrayTrait;

#[test]
fn test_empty() {}

#[test]
fn test_with_result() -> (felt, felt, felt, felt) {
    (1, 2, 3, 4)
}

#[test]
fn test_panic() {
    let mut data = array_new::<felt>();
    array_append::<felt>(ref data, 21);
    panic(data)
}

