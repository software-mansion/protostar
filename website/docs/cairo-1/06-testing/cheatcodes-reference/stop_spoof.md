# `stop_spoof`

```cairo
fn stop_spoof(contract_address: felt252) nopanic;
```

Stops a spoof started by [`start_spoof`](./start_spoof.md).

- `contract_address` address of the contract that was previously spoofed.

```cairo title="Example"
#[test]
fn test_stop_spoof() {
    stop_spoof(spoofed_contract_address).unwrap();
    // Contract is no longer spoofed from here
}
```
