use array::ArrayTrait;

fn fib(a: felt, b: felt, n: felt) -> felt {
    match gas::get_gas() {
        Option::Some(_) => {},
        Option::None(_) => {
            let mut data = array_new::<felt>();
            array_append::<felt>(ref data, 'OOG');
            panic(data);
        },
    }
    match n {
        0 => a,
        _ => fib(b, a + b, n - 1),
    }
}

#[test]
fn test_ec_op() {
    let f = fib(10, 10, 10);
}
