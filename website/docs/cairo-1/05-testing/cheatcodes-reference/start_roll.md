# `start_roll`

```cairo
fn start_roll(block_number: felt252, target_contract_address: felt252) -> Result::<(), felt252> nopanic;
```

Sets a block number for a [deployed](./deploy.md) contract, until [`stop_roll`](./stop_roll.md) is called.

- `block_number` - the new block number
- `target_contract_address` - address of the deployed contract, for which the block number will be set. 

:::note
The default `block_number` value in tests is set to -1 for every contract.
:::
 
## Usage example

### Tested contract
```cairo title="simple contract"
#[contract]
mod MinimalContract {
    use starknet::info::get_block_info;
    use box::BoxTrait;

    #[view]
    fn check_block_number() -> u64 {
        get_block_info().unbox().block_number
    }
}
```

### Test file
```cairo title="Example test"
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_start_roll() {
    let deployed_contract_address = deploy_contract('simple', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'check_block_number', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == -1, *result.at(0_u32));

    start_roll(100, deployed_contract_address);
    let result = call(deployed_contract_address, 'check_block_number', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}
```
