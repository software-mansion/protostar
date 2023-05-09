# `start_prank`

```cairo
fn start_prank(caller_address: felt252, target_contract_address: felt252) -> Result::<(), felt252> nopanic;
```

Changes a caller address returned by `get_caller_address()` for the targeted contract until the prank is stopped
with [stop_prank](./stop_prank.md).

- `caller_address` address that will start being returned by `get_caller_address()`
- `target_contract_address` address for which `get_caller_address()` result will be replaced

```cairo title="Example"
#[contract]
mod MyContract {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::ContractAddressIntoFelt252;
    use option::Option;
    use traits::Into;

    struct Storage {
        stored_value: felt252
    }

    #[external]
    fn will_be_pranked() {
        let caller_address: ContractAddress = get_caller_address();
        if (caller_address.into() == 123) {
            stored_value::write(100);
        } else {
            stored_value::write(50);
        }
    }
    
    #[view]
    fn get_stored_value() -> felt252 {
        stored_value::read()
    }
}

#[test]
fn my_test() {
    invoke(deployed_contract_address, 'will_be_pranked', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_stored_value', ArrayTrait::new()).unwrap();
    // Standard value is set
    assert(*return_data.at(0_u32) == 50, 'check call result');
    
    // Pranked the address
    start_prank(123, deployed_contract_address).unwrap();
    
    invoke(deployed_contract_address, 'will_be_pranked', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_stored_value', ArrayTrait::new()).unwrap();
    // Special value (100) is set
    assert(*return_data.at(0_u32) == 100, 'check call result');
}
```