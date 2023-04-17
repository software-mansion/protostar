use array::ArrayTrait;

fn fib(a: felt252, b: felt252, n: felt252) -> felt252 {
    match gas::withdraw_gas() {
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
