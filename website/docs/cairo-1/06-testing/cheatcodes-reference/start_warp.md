# `start_warp`

```cairo
fn start_warp(block_timestamp: felt252, target_contract_address: felt252) -> Result::<(), felt252> nopanic;
```

Sets a block timestamp for a [deployed](./deploy.md) contract, until [`stop_warp`](./stop_warp.md) is called.

- `block_timestamp` - value of the timestamp
- `target_contract_address` - address of the deployed contract, for which the block timestamp will be set. 

:::note
The default `block_timestamp` value in tests is set to 0 for every contract.
:::
 
## Usage example

### Tested contract
```cairo title="simple contract"
#[contract]
mod MinimalContract {
    use starknet::info::get_block_info;
    use box::BoxTrait;

    #[view]
    fn check_timestamp() -> u64 {
        get_block_info().unbox().block_timestamp
    }
}
```

### Test file
```cairo title="Example test"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_start_warp_simple() {
    let deployed_contract_address = deploy_contract('simple', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'check_timestamp', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 0, *result.at(0_u32));

    start_warp(100, deployed_contract_address);
    let result = call(deployed_contract_address, 'check_timestamp', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}
```
