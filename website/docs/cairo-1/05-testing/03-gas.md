---
sidebar_label: Gas
---

# Limiting gas

To limit gas available in a test case you can use `#[available_gas(x)]` attribute, replacing `x` with the desired limit.

Example:
```
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


// With no decorator gas is unlimited
#[test]
fn test_unlimited_gas() {
    assert(fib(0, 1, 10) == 55, 'invalid result');
}


// This test will pass
#[test]
#[available_gas(100000)]
fn test_enough_gas() {
    assert(fib(0, 1, 10) == 55, 'invalid result');
}


// This test will fail, due to not enough gas
#[test]
#[available_gas(1)]
fn test_not_enough_gas() {
    assert(fib(0, 1, 10) == 55, 'invalid result');
}
```

:::warning
All cheatcodes have cost `0` so validating gas cost makes sense only for [unit tests](./01-unit-testing.md).
:::