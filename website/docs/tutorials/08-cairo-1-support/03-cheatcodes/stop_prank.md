# `stop_prank`

```cairo
extern fn stop_prank(target_contract_address: felt252) -> Result::<(), felt252> nopanic;
```

Stops a prank started by [`start_prank`](./start_prank.md).

- `target_contract_address` address that was previously pranked.

```cairo title="Example"
#[test]
fn my_test() {
    stop_prank(pranked_address).unwrap();
    // Address is no longer pranked from here
}
```
