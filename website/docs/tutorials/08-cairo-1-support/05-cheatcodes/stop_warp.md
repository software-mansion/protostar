# `stop_warp`

```cairo
extern fn stop_warp(target_contract_address: felt252) -> Result::<(), felt252> nopanic;
```

Stops a warp started by [`start_warp`](./start_warp.md).

- `target_contract_address` address that was previously warped.

```cairo title="Example"
#[test]
fn my_test() {
    stop_prank(pranked_address).unwrap();
    // Block timestamp is no longer warped from here (defaults to 0)
}
```
