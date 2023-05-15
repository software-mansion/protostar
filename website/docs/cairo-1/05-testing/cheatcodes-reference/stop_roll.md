# `stop_roll`

```cairo
fn stop_roll(target_contract_address: felt252) -> Result::<(), felt252> nopanic;
```

Stops a roll started by [`start_roll`](./start_roll.md).

- `target_contract_address` address that was previously rolled.

```cairo title="Example"
#[test]
fn my_test() {
    stop_roll(rolled_address).unwrap();
    // Block number is no longer rolled from here (defaults to -1)
}
```
