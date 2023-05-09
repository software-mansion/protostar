use array::ArrayTrait;


fn fib(a: felt252, b: felt252, n: felt252) -> felt252 {
    match gas::withdraw_gas_all(get_builtin_costs()) {
        Option::Some(_) => {},
        Option::None(_) => {
            let mut data = ArrayTrait::new();
            data.append('Out of gas');
            panic(data);
        }
    }

    match n {
        0 => a,
        _ => fib(b, a + b, n - 1),
    }
}

#[test]
#[available_gas(100000)]
fn fibonacci_test() {
    assert(fib(0, 1, 10) == 55, 'invalid result');
}

#[test]
#[available_gas(1)]
fn fibonacci_test_out_of_gas_panic() {
    assert(fib(0, 1, 10) == 55, 'invalid result');
}

#[test]
fn fibonacci_test_infinite() {
    assert(fib(0, 1, 10) == 55, 'invalid result');
}
