#[test]
fn test_declare() {
    match declare('minimal') {
        Result::Ok(_) => (),
        Result::Err(x) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, x);
            panic(data)
        },
    }
}
