use array::ArrayTrait;

#[test]
fn test_ok() {}


#[test]
fn test_panic() {
    let mut data = array_new::<felt>();
    array_append::<felt>(ref data, 21);
    panic(data)
}

